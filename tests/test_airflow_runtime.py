"""Ready Airflow helpers: real files, no scheduler or ML imports required."""

import ast
import importlib.util
import json
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID
from course_tasks import load_task

import pytest


def runtime():
    spec = importlib.util.find_spec("housing.airflow_runtime")
    assert spec is not None, "Create housing.airflow_runtime"
    from housing import airflow_runtime

    return airflow_runtime


def config(tmp_path, monkeypatch, interval=None):
    r = runtime()
    monkeypatch.setattr(r, "training_revision", lambda: "source-v1")
    data = tmp_path / "data with spaces.csv"
    data.write_text("x,y\n1,2\n")
    return r.prepare_training(
        data, 42, output_root=tmp_path / "runs", interval=interval
    )


def artifacts(path, candidate=0.8):
    path.mkdir(parents=True, exist_ok=True)
    (path / "model.joblib").write_bytes(b"trusted fixture")
    for name, value in {
        "metrics.json": {
            "candidate": {"test": {"mae": candidate}},
            "baseline": {"test": {"mae": 1.0}},
        },
        "manifest.json": {"seed": 42},
        "split.json": {"train": [0]},
    }.items():
        (path / name).write_text(json.dumps(value))


def test_training_key_tracks_inputs_not_output_directory(tmp_path, monkeypatch):
    r = runtime()
    a = config(tmp_path, monkeypatch)
    b = r.prepare_training(a["data_path"], 42, output_root=tmp_path / "elsewhere")
    assert a["run_key"] == b["run_key"]
    assert a["path"] != b["path"]
    assert r.prepare_training(a["data_path"], 17)["run_key"] != a["run_key"]
    monkeypatch.setattr(r, "training_revision", lambda: "source-v2")
    assert r.prepare_training(a["data_path"], 42)["run_key"] != a["run_key"]
    Path(a["data_path"]).write_text("x,y\n1,3\n")
    assert r.prepare_training(a["data_path"], 42)["run_key"] != a["run_key"]


def test_interval_normalizes_and_changes_key(tmp_path, monkeypatch):
    r = runtime()
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end = datetime(2025, 1, 2, tzinfo=timezone.utc)
    interval = r.interval_metadata(start, end)
    assert interval == {
        "data_interval_start": start.isoformat(),
        "data_interval_end": end.isoformat(),
        "partition": "2025-01-01",
    }
    a = config(tmp_path, monkeypatch)
    b = r.prepare_training(a["data_path"], 42, interval=interval)
    assert a["run_key"] != b["run_key"]
    assert (
        r.prepare_training(a["data_path"], 42, interval=interval)["run_key"]
        == b["run_key"]
    )
    with pytest.raises(ValueError):
        r.interval_metadata(start.replace(tzinfo=None), end)
    with pytest.raises(ValueError):
        r.interval_metadata(start, start)


def test_real_cli_boundary_and_metadata(tmp_path, monkeypatch):
    r = runtime()
    interval = r.interval_metadata(
        datetime(2025, 1, 1, tzinfo=timezone.utc),
        datetime(2025, 1, 2, tzinfo=timezone.utc),
    )
    c = config(tmp_path, monkeypatch, interval)
    before = json.loads(json.dumps(c))
    calls = []

    def run(command, **kw):
        calls.append(command)
        assert command[0] == "/opt/housing-venv/bin/python"
        assert command[-3:] == [c["data_path"], c["path"], "42"]
        assert kw["check"] is True and not kw.get("shell")
        artifacts(Path(c["path"]))
        return subprocess.CompletedProcess(
            command, 0, 'training log\nCOURSE_TRAIN_RESULT={"model_version":"v7"}\n', ""
        )

    monkeypatch.setattr(r.subprocess, "run", run)
    result = r.run_training(c)
    assert result == {"path": c["path"], "run_key": c["run_key"], "model_version": "v7"}
    assert c == before and len(calls) == 1
    saved = json.loads((Path(c["path"]) / "orchestration.json").read_text())
    assert saved["interval"] == interval and saved["run_key"] == c["run_key"]


@pytest.mark.parametrize(
    "missing", ["model.joblib", "metrics.json", "manifest.json", "split.json"]
)
def test_success_without_complete_artifacts_is_not_success(
    tmp_path, monkeypatch, missing
):
    r = runtime()
    c = config(tmp_path, monkeypatch)

    def run(command, **kw):
        artifacts(Path(c["path"]))
        (Path(c["path"]) / missing).unlink()
        return subprocess.CompletedProcess(
            command, 0, 'COURSE_TRAIN_RESULT={"model_version":"v1"}\n', ""
        )

    monkeypatch.setattr(r.subprocess, "run", run)
    with pytest.raises((ValueError, FileNotFoundError)):
        r.run_training(c)


def test_failed_process_and_changed_input_are_not_published(
    tmp_path, monkeypatch, caplog
):
    r = runtime()
    c = config(tmp_path, monkeypatch)

    def fail(*a, **kw):
        raise subprocess.CalledProcessError(1, a[0], stderr="train failed")

    monkeypatch.setattr(r.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        r.run_training(c)
    assert "train failed" in caplog.text
    Path(c["data_path"]).write_text("different")
    with pytest.raises(ValueError, match="changed"):
        r.run_training(c)
    assert not Path(c["path"]).exists()


def test_gate_and_idempotent_release(tmp_path):
    r = runtime()
    out = tmp_path / "run"
    artifacts(out)
    metadata = {"path": str(out), "run_key": "run-1", "model_version": "v7"}
    assert r.quality_gate(metadata) is True
    assert r.quality_gate(metadata, ratio=0.0) is False
    releases = tmp_path / "nested" / "releases"
    expected = {
        "run_key": "run-1",
        "model_path": str(out / "model.joblib"),
        "model_version": "v7",
    }
    assert r.publish_release(metadata, releases) == expected
    path = releases / "run-1.json"
    before = path.read_bytes()
    assert r.publish_release(metadata, releases) == expected
    assert path.read_bytes() == before and len(list(releases.glob("*.json"))) == 1
    with pytest.raises(ValueError):
        r.publish_release({**metadata, "model_version": "other"}, releases)
    assert path.read_bytes() == before


@pytest.mark.parametrize("value", [True, -1, "0.8", float("nan"), float("inf")])
def test_gate_rejects_invalid_measurements(tmp_path, value):
    r = runtime()
    artifacts(tmp_path, value)
    with pytest.raises(ValueError):
        r.quality_gate({"path": str(tmp_path)})


def test_failed_replace_and_unsafe_key_leave_no_release(tmp_path, monkeypatch):
    r = runtime()
    out = tmp_path / "run"
    artifacts(out)
    m = {"path": str(out), "run_key": "run", "model_version": "v1"}
    releases = tmp_path / "releases"
    with pytest.raises(ValueError):
        r.publish_release({**m, "run_key": "../escape"}, releases)

    def fail(*args):
        raise OSError("disk full")

    monkeypatch.setattr(r.os, "replace", fail)
    with pytest.raises(OSError, match="disk full"):
        r.publish_release(m, releases)
    assert not list(releases.iterdir())


def test_airflow_test_harness_embedded_python_has_valid_syntax():
    source = Path(__file__).resolve().parents[1] / "modules/05-airflow/conftest.py"
    tree = ast.parse(source.read_text())
    scripts = [
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "dedent"
        and node.args
        and isinstance(node.args[0], ast.Constant)
    ]
    assert scripts
    for script in scripts:
        ast.parse(textwrap.dedent(script))


def test_acceptance_requires_release_before_first_failure():
    checks = load_task("05-airflow/02-gate-retry", filename="test_airflow.py")
    assert hasattr(checks, "assert_publication_precedes_failure")
    checks.assert_publication_precedes_failure(
        10.0, {"first_failure_at": 11.0, "second_started_at": 12.0}
    )
    with pytest.raises(AssertionError):
        checks.assert_publication_precedes_failure(
            13.0, {"first_failure_at": 11.0, "second_started_at": 12.0}
        )


def test_live_acceptance_uses_fresh_logical_dates(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "course_airflow_fixtures",
        Path(__file__).resolve().parents[1] / "modules/05-airflow/conftest.py",
    )
    fixtures = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixtures)
    assert hasattr(fixtures, "acceptance_logical_date")
    first, second = (
        fixtures.acceptance_logical_date(),
        fixtures.acceptance_logical_date(),
    )
    assert first != second
    assert datetime.fromisoformat(first).utcoffset().total_seconds() == 0

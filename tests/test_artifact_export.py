"""Ready exporters copy fixtures; student solutions are never executed."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from course_tasks import load_task
from course_tasks.artifacts import export_files

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def bundle(tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "work" / "artifacts"
    source.mkdir()
    names = ["metrics.json", "manifest.json", "split.json", "model.joblib"]
    for name in names:
        (source / name).write_bytes(
            b'{"fixture": true}\n'
            if name.endswith(".json")
            else b"not a pickle: copy only"
        )
    return [(source / name, destination / name) for name in names]


def test_copy_creates_destination_and_preserves_bytes(bundle):
    assert export_files(bundle) == [target for _, target in bundle]
    for source, target in bundle:
        assert source.read_bytes() == target.read_bytes()


@pytest.mark.parametrize("invalid", ["missing", "empty", "json", "nan"])
def test_invalid_complete_set_leaves_destination_untouched(bundle, invalid):
    for _, target in bundle:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"previous")
    source = bundle[-1][0] if invalid in {"missing", "empty"} else bundle[0][0]
    if invalid == "missing":
        source.unlink()
    else:
        source.write_text(
            {"empty": "", "json": "{broken", "nan": '{"metric": NaN}'}[invalid]
        )
    with pytest.raises((ValueError, OSError)):
        export_files(bundle, replace=True)
    assert all(target.read_bytes() == b"previous" for _, target in bundle)


def test_all_conflicts_are_reported_before_any_copy(bundle):
    for _, target in bundle[:2]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"previous")
    with pytest.raises(FileExistsError) as error:
        export_files(bundle)
    assert all(target.name in str(error.value) for _, target in bundle[:2])
    assert "--replace" in str(error.value)
    assert all(target.read_bytes() == b"previous" for _, target in bundle[:2])
    assert all(not target.exists() for _, target in bundle[2:])


def test_identical_export_does_not_touch_files(bundle):
    export_files(bundle)
    stamps = [target.stat().st_mtime_ns for _, target in bundle]
    assert export_files(bundle) == []
    assert [target.stat().st_mtime_ns for _, target in bundle] == stamps


def test_replace_updates_only_declared_files(bundle):
    export_files(bundle)
    other = bundle[0][1].parent / "notes.txt"
    other.write_text("keep me")
    bundle[-1][0].write_bytes(b"a different model")
    assert export_files(bundle, replace=True) == [bundle[-1][1]]
    assert bundle[-1][1].read_bytes() == b"a different model"
    assert other.read_text() == "keep me"


def test_copy_failure_preserves_previous_files_and_removes_temporary_files(
    bundle, monkeypatch
):
    for _, target in bundle:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"previous")
    original = shutil.copy2

    def fail_on_model(source, target):
        if source.name == "model.joblib":
            raise OSError("simulated full disk")
        return original(source, target)

    monkeypatch.setattr(shutil, "copy2", fail_on_model)
    with pytest.raises(OSError, match="full disk"):
        export_files(bundle, replace=True)
    assert all(target.read_bytes() == b"previous" for _, target in bundle)
    assert sorted(p.name for p in bundle[0][1].parent.iterdir()) == sorted(
        target.name for _, target in bundle
    )


def test_replacements_follow_declared_order_with_model_last(bundle, monkeypatch):
    observed = []
    original = os.replace

    def record(source, target):
        assert Path(source).parent == target.parent
        observed.append(target.name)
        return original(source, target)

    monkeypatch.setattr(os, "replace", record)
    export_files(bundle)
    assert observed == ["metrics.json", "manifest.json", "split.json", "model.joblib"]


def test_task_cli_from_another_directory_without_running_solution(tmp_path):
    module, slug = "15-triton", "01-onnx"
    task = tmp_path / "modules" / module / "tasks" / slug
    (task / "output").mkdir(parents=True)
    (tmp_path / "modules/tasks.json").write_text(
        json.dumps({"schema_version": 1, "tasks": []})
    )
    shutil.copy2(
        ROOT / "modules" / module / "tasks" / slug / "export.py", task / "export.py"
    )
    (task / "solution.py").write_text(
        "raise AssertionError('export must not run the solution')\n"
    )
    sources = {
        "config.pbtxt": "triton/model_repository/housing/config.pbtxt",
        "output/model.onnx": "triton/model_repository/housing/1/model.onnx",
    }
    for source in sources:
        (task / source).write_bytes(
            b'{"fixture": true}' if source.endswith(".json") else b"fixture bytes"
        )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    environment = os.environ.copy()
    environment["MLOPS_COURSE_ROOT"] = str(tmp_path)

    def invoke(*args):
        return subprocess.run(
            [sys.executable, str(task / "export.py"), *args],
            cwd=elsewhere,
            env=environment,
            text=True,
            capture_output=True,
        )

    result = invoke()
    assert result.returncode == 0, result.stderr
    assert "перезапуст" in result.stdout.lower()
    for source, target in sources.items():
        destination = tmp_path / "work" / target
        assert destination.read_bytes() == (task / source).read_bytes()
        assert str(destination) in result.stdout
    assert invoke().returncode == 0
    model = task / ("output/model.joblib" if module == "01-ml" else "output/model.onnx")
    model.write_bytes(b"updated model")
    result = invoke()
    assert result.returncode != 0 and "--replace" in result.stderr
    assert "Traceback" not in result.stderr
    assert invoke("--replace").returncode == 0
    destination = tmp_path / "work" / list(sources.values())[-1]
    assert destination.read_bytes() == b"updated model"


def test_onnx_default_output_is_task_local(tmp_path, monkeypatch):
    solution = load_task("15-triton/01-onnx")
    observed = []
    monkeypatch.setattr(
        solution, "export_bundle", lambda bundle, output: observed.append(output)
    )
    monkeypatch.setattr(sys, "argv", ["solution.py"])
    monkeypatch.chdir(tmp_path)
    solution.main()
    assert observed == [ROOT / "modules/15-triton/tasks/01-onnx/output/model.onnx"]

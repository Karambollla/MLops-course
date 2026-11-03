"""Offline проверки поведения; исходная заготовка должна быть RED."""

import os
import subprocess
from pathlib import Path

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


@pytest.mark.parametrize("seed", [42, 17, 901])
def test_training_uses_cli_and_metadata(tmp_path, monkeypatch, seed):
    data = tmp_path / "input with spaces.csv"
    data.write_text("x\n1\n")
    out = tmp_path / "runs" / "key-1"
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        assert isinstance(command, list) and kwargs.get("check") is True
        assert not kwargs.get("shell", False)
        assert command[:3] == ["/opt/housing-venv/bin/python", "-m", "housing.train"]
        assert command[command.index("--data") + 1] == str(data)
        assert command[command.index("--output") + 1] == str(out)
        assert len(command) == 9
        assert dict(zip(command[3::2], command[4::2])) == {
            "--data": str(data),
            "--output": str(out),
            "--seed": str(seed),
        }
        out.mkdir(parents=True, exist_ok=True)
        for name in ["model.joblib", "metrics.json", "manifest.json", "split.json"]:
            (out / name).write_text("{}")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert s.run_training(data, out, seed) == {"path": str(out), "run_key": "key-1"}
    assert len(calls) == 1


def test_failed_training_propagates(tmp_path, monkeypatch):
    data = tmp_path / "input.csv"
    data.touch()

    def failure(*a, **kw):
        raise subprocess.CalledProcessError(1, a[0])

    monkeypatch.setattr(subprocess, "run", failure)
    with pytest.raises(subprocess.CalledProcessError):
        s.run_training(data, tmp_path / "out")


@pytest.mark.parametrize(
    "missing", ["model.joblib", "metrics.json", "manifest.json", "split.json"]
)
def test_successful_process_requires_every_artifact(tmp_path, monkeypatch, missing):
    output = tmp_path / "runs" / "key"

    def incomplete(command, **kwargs):
        output.mkdir(parents=True)
        for name in ["model.joblib", "metrics.json", "manifest.json", "split.json"]:
            if name != missing:
                (output / name).write_text("{}")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", incomplete)
    try:
        s.run_training(tmp_path / "data.csv", output, 17)
    except NotImplementedError:
        raise
    except (FileNotFoundError, ValueError, RuntimeError):
        pass
    else:
        pytest.fail(f"Successful process did not produce required {missing}")


@pytest.mark.integration
def test_dag_loads_with_real_airflow_sdk_in_running_container():
    """Read-only DagBag parse; never starts a service or executes a learner task."""
    if os.getenv("MLOPS_RUN_INTEGRATION") != "1":
        pytest.skip(
            "Set MLOPS_RUN_INTEGRATION=1 with an already running Airflow container"
        )
    root = Path(__file__).resolve().parents[4]
    script = """
import airflow
from airflow.models.dagbag import DagBag
assert airflow.__version__ == "3.1.0", airflow.__version__
bag = DagBag(dag_folder="/opt/airflow/dags/housing_pipeline.py", include_examples=False)
assert not bag.import_errors, bag.import_errors
dag = bag.dags.get("housing_pipeline")
assert dag is not None
assert {"validate_data", "train_evaluate", "gate", "publish"} <= set(dag.task_ids)
assert "train_evaluate" in dag.get_task("validate_data").downstream_task_ids
assert "gate" in dag.get_task("train_evaluate").downstream_task_ids
assert "publish" in dag.get_task("gate").downstream_task_ids
assert dag.get_task("publish").retries >= 1
"""
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(root / "labs/airflow/compose.yaml"),
            "exec",
            "-T",
            "airflow",
            "python",
            "-c",
            script,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr

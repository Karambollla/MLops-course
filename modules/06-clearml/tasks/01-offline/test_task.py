"""Check student's SDK calls against varying actual training outputs, without ClearML."""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import housing
import pytest
from course_tasks import load_solution

solution = load_solution(__file__)


@pytest.mark.parametrize("seed,mae,rmse", [(17, 0.31, 0.57), (91, 0.72, 0.95)])
def test_training_logs_actual_outputs(tmp_path, monkeypatch, seed, mae, rmse):
    data = tmp_path / "data.csv"
    data.write_text(f"fixture-for-logging-{seed}\n")
    output = tmp_path / "bundle"
    calls = []

    def train(data_arg, output_arg, seed_arg):
        calls.append((Path(data_arg), Path(output_arg), seed_arg))
        output.mkdir()
        (output / "model.joblib").write_bytes(b"opaque-test-artifact")
        (output / "manifest.json").write_text(
            json.dumps(
                {
                    "seed": seed,
                    "data_sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
                }
            )
        )
        (output / "metrics.json").write_text(
            json.dumps({"candidate": {"test": {"mae": mae, "rmse": rmse}}})
        )

    # Training is independently exercised in module 01; this fixture tests logging wiring.
    training = SimpleNamespace(train=train)
    monkeypatch.setitem(sys.modules, "housing.train", training)
    monkeypatch.setattr(housing, "train", training, raising=False)

    class Task:
        def __init__(self):
            self.params = {}
            self.scalars = []
            self.artifacts = {}

        def connect(self, values):
            self.params.update(values)

        def get_logger(self):
            return self

        def report_scalar(self, title, series, value, iteration):
            self.scalars.append((title, series, value, iteration))

        def upload_artifact(self, name, artifact_object):
            self.artifacts[name] = Path(artifact_object).read_bytes()

    task = Task()
    solution.train_and_log(task, data, output, seed)
    assert calls == [(data, output, seed)]
    assert task.params["seed"] == seed
    assert task.params["data_sha256"] == hashlib.sha256(data.read_bytes()).hexdigest()
    assert ("quality", "mae", mae, 0) in task.scalars
    assert ("quality", "rmse", rmse, 0) in task.scalars
    for name in ("model.joblib", "manifest.json"):
        assert task.artifacts[name] == (output / name).read_bytes()


def test_training_failure_is_propagated(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("training failed")

    training = SimpleNamespace(train=fail)
    monkeypatch.setitem(sys.modules, "housing.train", training)
    monkeypatch.setattr(housing, "train", training, raising=False)
    data = tmp_path / "data.csv"
    data.write_text("fixture-for-training-failure\n")
    task = SimpleNamespace(connect=lambda values: None)
    with pytest.raises(RuntimeError, match="training failed"):
        solution.train_and_log(task, data, tmp_path / "output")


def test_main_closes_sdk_task_when_training_fails(tmp_path, monkeypatch):
    events = []

    class SDKTask:
        @staticmethod
        def running_locally():
            return True

        @staticmethod
        def set_offline(offline_mode):
            events.append(("offline", offline_mode))

        @staticmethod
        def init(**kwargs):
            return SimpleNamespace(close=lambda: events.append(("closed", True)))

    def fail(*args, **kwargs):
        raise RuntimeError("injected training failure")

    monkeypatch.setattr(solution, "Task", SDKTask)
    monkeypatch.setenv("CLEARML_OFFLINE_MODE", "1")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "solution.py",
            "--data",
            str(tmp_path / "data.csv"),
            "--output",
            str(tmp_path / "bundle"),
        ],
    )
    monkeypatch.setattr(solution, "train_and_log", fail)
    with pytest.raises(RuntimeError, match="injected training failure"):
        solution.main()
    assert events == [("offline", True), ("closed", True)]


def test_main_closes_sdk_task_after_success(tmp_path, monkeypatch):
    events = []
    task = SimpleNamespace(close=lambda: events.append("closed"))

    class SDKTask:
        running_locally = staticmethod(lambda: True)
        set_offline = staticmethod(lambda offline_mode: None)
        init = staticmethod(lambda **kwargs: task)

    data, output = tmp_path / "data.csv", tmp_path / "bundle"

    def trained(actual_task, actual_data, actual_output, seed):
        assert (actual_task, actual_data, actual_output, seed) == (
            task,
            data,
            output,
            17,
        )
        events.append("trained")
        return "training-result"

    monkeypatch.setattr(solution, "Task", SDKTask)
    monkeypatch.setattr(solution, "train_and_log", trained)
    monkeypatch.setattr(
        sys,
        "argv",
        ["solution.py", "--data", str(data), "--output", str(output), "--seed", "17"],
    )
    assert solution.main() == "training-result"
    assert events == ["trained", "closed"]


@pytest.mark.sdk
@pytest.mark.parametrize("seed", [29, 83])
def test_real_offline_sdk_persists_params_scalars_and_output_artifacts(tmp_path, seed):
    if os.getenv("MLOPS_RUN_SDK") != "1":
        pytest.skip("Set MLOPS_RUN_SDK=1 for the pinned real offline ClearML SDK")
    if importlib.util.find_spec("clearml") is None:
        pytest.fail("Install labs/clearml/requirements.txt before enabling SDK tests")
    env = dict(os.environ)
    env.update(
        {
            "CLEARML_OFFLINE_MODE": "1",
            "CLEARML_CACHE_DIR": str(tmp_path / "cache"),
            "CLEARML_CONFIG_FILE": str(tmp_path / "clearml.conf"),
        }
    )
    # Do not inherit credentials/remote-task state; offline tests need no server.
    for key in list(env):
        if key.startswith(("CLEARML_API_", "CLEARML_TASK_", "CLEARML_PROC_")):
            env.pop(key)
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("sdk_offline_probe.py")),
            str(tmp_path),
            str(seed),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr

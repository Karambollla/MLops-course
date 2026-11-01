"""Check student's SDK calls against varying actual training outputs, without ClearML."""

import hashlib
import json
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

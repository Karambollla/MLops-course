"""Offline проверки поведения; исходная заготовка должна быть RED."""

import json

import joblib
import pandas as pd
import pytest
from course_tasks import load_solution, read_json
from housing.features import FEATURES

s = load_solution(__file__)


class Constant:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        return [self.value] * len(X)


def run_dir(path, value=1.0, digest="a" * 64):
    path.mkdir()
    split = {"train": [0], "validation": [1], "test": [2]}
    manifest = {
        "seed": 42,
        "data_sha256": digest,
        "feature_order": FEATURES,
        "parameters": {"x": 1},
        "split": split,
        "versions": {"python": "test"},
    }
    metrics = {
        model: {part: {"mae": 0.5, "rmse": 0.6} for part in ["validation", "test"]}
        for model in ["baseline", "candidate"]
    }
    for name, obj in [("manifest", manifest), ("split", split), ("metrics", metrics)]:
        (path / f"{name}.json").write_text(json.dumps(obj))
    joblib.dump(
        {
            "schema_version": 1,
            "pipeline": Constant(value),
            "features": FEATURES,
            "model_version": "v1",
        },
        path / "model.joblib",
    )
    return path


def test_reproduction_and_real_difference(tmp_path):
    batch = pd.DataFrame([[1] * 8] * 20, columns=FEATURES)
    a = run_dir(tmp_path / "a")
    b = run_dir(tmp_path / "b", 1.0 + 1e-9)
    assert s.compare_runs(a, b, batch) == {
        "predictions_equal": True,
        "metrics_equal": True,
    }
    c = run_dir(tmp_path / "c", 2.0)
    assert s.compare_runs(a, c, batch) == {
        "predictions_equal": False,
        "metrics_equal": True,
    }
    metrics = read_json(c / "metrics.json")
    metrics["candidate"]["test"]["mae"] = 2.0
    (c / "metrics.json").write_text(json.dumps(metrics))
    assert s.compare_runs(a, c, batch)["metrics_equal"] is False


def test_provenance_rejection(tmp_path):
    batch = pd.DataFrame([[1] * 8] * 20, columns=FEATURES)
    a = run_dir(tmp_path / "a")
    b = run_dir(tmp_path / "b", digest="b" * 64)
    with pytest.raises(ValueError):
        s.compare_runs(a, b, batch)
    with pytest.raises(ValueError):
        s.compare_runs(a, a, batch[FEATURES[::-1]])

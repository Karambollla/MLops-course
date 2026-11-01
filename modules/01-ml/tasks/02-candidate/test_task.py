"""Offline проверки поведения; исходная заготовка должна быть RED."""

import hashlib

import joblib
import numpy as np
import pandas as pd
import pytest
from course_tasks import load_solution, read_json
from housing.features import FEATURES, TARGET
from sklearn.pipeline import Pipeline

s = load_solution(__file__)


def test_pipeline_fits_and_roundtrips(tmp_path):
    rng = np.random.default_rng(42)
    X = pd.DataFrame(rng.normal(size=(80, 8)), columns=FEATURES)
    y = 2 * X["MedInc"] + X["Latitude"]
    p = s.build_pipeline(42)
    assert isinstance(p, Pipeline)
    p.fit(X.iloc[:60], y.iloc[:60])
    pred = p.predict(X.iloc[60:])
    assert pred.shape == (20,) and np.isfinite(pred).all()
    joblib.dump(p, tmp_path / "p.joblib")
    assert np.allclose(pred, joblib.load(tmp_path / "p.joblib").predict(X.iloc[60:]))


def test_training_artifacts_and_repeat(tmp_path):
    rng = np.random.default_rng(7)
    frame = pd.DataFrame(rng.uniform(1, 3, (100, 8)), columns=FEATURES)
    frame[TARGET] = 2 * frame.MedInc + frame.Latitude
    path = tmp_path / "input.csv"
    frame.to_csv(path, index=False)
    outputs = [tmp_path / "one", tmp_path / "two"]
    predictions = []
    for out in outputs:
        s.train(path, out, 42)
        bundle = joblib.load(out / "model.joblib")
        assert bundle["schema_version"] == 1 and bundle["features"] == FEATURES
        assert isinstance(bundle["model_version"], str) and bundle["model_version"]
        predictions.append(bundle["pipeline"].predict(frame[FEATURES].iloc[:20]))
        metrics = read_json(out / "metrics.json")
        for model in ["baseline", "candidate"]:
            for part in ["validation", "test"]:
                assert set(metrics[model][part]) == {"mae", "rmse"}
                assert all(
                    np.isfinite(v) and v >= 0 for v in metrics[model][part].values()
                )
        manifest = read_json(out / "manifest.json")
        assert manifest["data_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert manifest["seed"] == 42 and manifest["feature_order"] == FEATURES
        assert manifest["versions"] and manifest["parameters"]
        split = read_json(out / "split.json")
        assert manifest["split"] == split
        assert sorted(sum(split.values(), [])) == list(range(100))
        for part in ["validation", "test"]:
            positions = split[part]
            truth = frame[TARGET].iloc[positions].to_numpy()
            predictions_for_part = bundle["pipeline"].predict(
                frame[FEATURES].iloc[positions]
            )
            baseline_mean = frame[TARGET].iloc[split["train"]].mean()
            for model, predicted in [
                ("candidate", predictions_for_part),
                ("baseline", np.full(len(positions), baseline_mean)),
            ]:
                errors = truth - predicted
                assert metrics[model][part] == {
                    "mae": pytest.approx(np.abs(errors).mean()),
                    "rmse": pytest.approx(np.sqrt(np.square(errors).mean())),
                }
        assert all(
            (out / name).stat().st_size > 0
            for name in ["model.joblib", "metrics.json", "manifest.json", "split.json"]
        )
    assert read_json(outputs[0] / "split.json") == read_json(outputs[1] / "split.json")
    assert np.allclose(*predictions, rtol=1e-6, atol=1e-8)


def test_failed_model_serialization_preserves_previous_model(tmp_path, monkeypatch):
    rng = np.random.default_rng(71)
    frame = pd.DataFrame(rng.normal(size=(40, len(FEATURES))), columns=FEATURES)
    frame[TARGET] = frame.MedInc * 2 + frame.Latitude
    data = tmp_path / "input.csv"
    frame.to_csv(data, index=False)
    output = tmp_path / "active"
    s.train(data, output, 42)
    model = output / "model.joblib"
    previous_bytes = model.read_bytes()
    previous_predictions = joblib.load(model)["pipeline"].predict(frame[FEATURES])

    serialization_attempts = []

    def failing_state(self):
        serialization_attempts.append(self)
        raise OSError("simulated serialization failure")

    # Fail serialization itself, independent of temporary-file names, file
    # handles, and the chosen pickle-compatible persistence function.
    monkeypatch.setattr(Pipeline, "__getstate__", failing_state)
    with pytest.raises(Exception) as failure:
        s.train(data, output, 7)
    assert serialization_attempts
    assert not isinstance(failure.value, NotImplementedError)
    assert model.read_bytes() == previous_bytes
    assert np.allclose(
        joblib.load(model)["pipeline"].predict(frame[FEATURES]), previous_predictions
    )

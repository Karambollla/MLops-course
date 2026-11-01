"""Offline проверки поведения; исходная заготовка должна быть RED."""

import hashlib

import joblib
import numpy as np
import pandas as pd
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
    assert read_json(outputs[0] / "split.json") == read_json(outputs[1] / "split.json")
    assert np.allclose(*predictions, rtol=1e-6, atol=1e-8)

"""Offline проверки поведения; исходная заготовка должна быть RED."""

import housing.api as api
import joblib
import pandas as pd
import pytest
from course_tasks import load_solution
from fastapi.testclient import TestClient
from housing.features import FEATURES
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import make_pipeline

s = load_solution(__file__)


def test_prediction_contract():
    response = {
        "predictions": [1.0, 2.0],
        "model_version": "v1",
        "target_unit": "100000 USD",
    }
    assert s.check_prediction_response(response, [1.0, 2.0], "v1") is None


@pytest.mark.parametrize(
    "change",
    [
        {"predictions": [1.0]},
        {"predictions": [1.0, float("nan")]},
        {"predictions": [1.0, 9.0]},
        {"model_version": "other"},
        {"target_unit": "USD"},
        {"extra": 1},
    ],
)
def test_invalid_prediction_contract(change):
    response = {
        "predictions": [1.0, 2.0],
        "model_version": "v1",
        "target_unit": "100000 USD",
    }
    response.update(change)
    with pytest.raises(ValueError):
        s.check_prediction_response(response, [1.0, 2.0], "v1")


def test_real_api(tmp_path, monkeypatch):
    batch = pd.DataFrame([[1.0] * 8, [2.0] * 8], columns=FEATURES)
    pipeline = make_pipeline(DummyRegressor()).fit(batch, [1.0, 3.0])
    path = tmp_path / "model.joblib"
    joblib.dump(
        {
            "schema_version": 1,
            "pipeline": pipeline,
            "features": FEATURES,
            "model_version": "test",
        },
        path,
    )
    monkeypatch.setenv("MODEL_PATH", str(path))
    with TestClient(api.create_app(path)) as client:
        assert client.get("/ready").status_code == 200
        assert s.exercise_api(client, pipeline, batch, "test") is None
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "absent.joblib"))
    with TestClient(api.create_app(tmp_path / "absent.joblib")) as client:
        assert client.get("/live").status_code == 200
        assert client.get("/ready").status_code == 503
        assert (
            client.post(
                "/predict", json={"instances": batch.to_dict("records")}
            ).status_code
            == 503
        )
    joblib.dump({"schema_version": 2}, path)
    monkeypatch.setenv("MODEL_PATH", str(path))
    with pytest.raises((ValueError, RuntimeError)):
        with TestClient(api.create_app(path)):
            pass

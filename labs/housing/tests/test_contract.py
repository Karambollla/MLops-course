import json

import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from housing.api import create_app
from housing.features import FEATURES as FEATURE_ORDER
from sklearn.linear_model import LinearRegression

FEATURES = {
    "MedInc": 3.0,
    "HouseAge": 20.0,
    "AveRooms": 5.0,
    "AveBedrms": 1.0,
    "Population": 1000.0,
    "AveOccup": 3.0,
    "Latitude": 34.0,
    "Longitude": -118.0,
}


def test_alive_but_not_ready_without_model(tmp_path):
    with TestClient(create_app(tmp_path / "missing.joblib")) as client:
        assert client.get("/live").status_code == 201
        assert client.get("/ready").status_code == 503
        assert (
            client.post("/predict", json={"instances": [FEATURES]}).status_code == 503
        )


def test_invalid_requests_are_rejected_before_inference(tmp_path):
    with TestClient(create_app(tmp_path / "missing.joblib")) as client:
        invalid = [
            {"instances": []},
            {"instances": [{"MedInc": 3.0}]},
            {"instances": [{**FEATURES, "extra": 1.0}]},
            {"instances": [{**FEATURES, "MedInc": "3"}]},
            {"instances": [FEATURES] * 257},
        ]
        for payload in invalid:
            assert client.post("/predict", json=payload).status_code == 422


def test_metrics_expose_request_count(tmp_path):
    with TestClient(create_app(tmp_path / "missing.joblib")) as client:
        client.get("/live")
        text = client.get("/metrics").text
        assert 'http_requests_total{route="/live",status="200"} 1.0' in text


def test_real_bundle_predicts_in_canonical_order(tmp_path):
    rng = np.random.default_rng(42)
    training = pd.DataFrame(rng.normal(size=(30, 8)), columns=FEATURE_ORDER)
    model = LinearRegression().fit(
        training, 2 * training["MedInc"] + training["HouseAge"]
    )
    frame = pd.DataFrame([FEATURES], columns=FEATURE_ORDER)
    path = tmp_path / "model.joblib"
    joblib.dump(
        {
            "schema_version": 1,
            "pipeline": model,
            "features": FEATURE_ORDER,
            "model_version": "test-v1",
        },
        path,
    )
    reversed_keys = dict(reversed(list(FEATURES.items())))
    with TestClient(create_app(path)) as client:
        response = client.post("/predict", json={"instances": [reversed_keys]})
        assert response.status_code == 200
        assert response.json()["model_version"] == "test-v1"
        np.testing.assert_allclose(
            response.json()["predictions"], model.predict(frame.iloc[:1])
        )
        assert client.get("/ready").status_code == 200


def test_incompatible_artifact_is_rejected_at_startup(tmp_path):
    path = tmp_path / "bad.joblib"
    joblib.dump({"schema_version": 1, "features": ["wrong"]}, path)
    with pytest.raises(RuntimeError, match="Несовместимый bundle"):
        with TestClient(create_app(path)):
            pass


def test_nonfinite_json_numbers_return_422_instead_of_500(tmp_path):
    with TestClient(
        create_app(tmp_path / "missing.joblib"), raise_server_exceptions=False
    ) as client:
        for value in [float("nan"), float("inf"), float("-inf")]:
            payload = json.dumps({"instances": [{**FEATURES, "MedInc": value}]})
            response = client.post(
                "/predict",
                content=payload,
                headers={"Content-Type": "application/json"},
            )
            assert response.status_code == 422

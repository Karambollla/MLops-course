"""Read-only checks against the student's running Docker container and API."""

import json
import math
import os
import subprocess
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture
def running():
    if os.environ.get("MLOPS_RUN_INTEGRATION") != "1":
        pytest.skip(
            "Запусти Compose и включи MLOPS_RUN_INTEGRATION=1 по README задания"
        )
    container = os.environ.get("MLOPS_CONTAINER_ID")
    assert container, "Укажи MLOPS_CONTAINER_ID из docker compose ps -q api"
    result = subprocess.run(
        ["docker", "inspect", container],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    inspected = json.loads(result.stdout)
    assert len(inspected) == 1 and inspected[0]["State"]["Running"]
    state = os.environ.get("MLOPS_MODEL_STATE", "ready")
    assert state in {"ready", "absent"}, "MLOPS_MODEL_STATE: ready или absent"
    return (
        inspected[0],
        os.getenv("MLOPS_HOUSING_URL", "http://127.0.0.1:8000").rstrip("/"),
        state,
    )


def request(base, path, payload=None):
    req = Request(
        base + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"},
    )
    try:
        response = urlopen(req, timeout=10)
    except HTTPError as error:
        response = error
    with response:
        return response.status, json.loads(response.read())


def test_actual_container_is_non_root_with_read_only_models(running):
    info, _, _ = running
    uid = subprocess.run(
        ["docker", "exec", info["Id"], "id", "-u"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout.strip()
    assert uid.isdigit() and uid != "0"
    assert any(
        mount["Destination"] == "/models" and mount["RW"] is False
        for mount in info["Mounts"]
    )
    image = subprocess.run(
        ["docker", "image", "inspect", info["Image"]],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    data = json.loads(image.stdout)[0]
    assert data["Id"] == info["Image"] and data["Size"] > 0


def test_live_ready_predict_and_invalid_input(running):
    _, base, state = running
    assert request(base, "/live")[0] == 200
    expected = 200 if state == "ready" else 503
    assert request(base, "/ready")[0] == expected
    payload = json.loads((ROOT / "labs/housing/request.json").read_text())
    status, body = request(base, "/predict", payload)
    assert status == expected
    if state == "ready":
        values = body["predictions"]
        assert len(values) == len(payload["instances"])
        assert all(
            isinstance(value, (float, int))
            and not isinstance(value, bool)
            and math.isfinite(value)
            for value in values
        )
        assert body["model_version"] and body["target_unit"] == "100000 USD"
    assert request(base, "/predict", {"instances": []})[0] == 422

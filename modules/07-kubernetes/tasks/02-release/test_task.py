"""Read the ready immutable release and send inference through its Service."""

import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_ready_release_and_service_prediction(kube, http):
    expected = os.getenv("MLOPS_EXPECTED_MODEL_VERSION")
    assert expected, (
        "Set MLOPS_EXPECTED_MODEL_VERSION from your trusted v1 bundle before running"
    )
    deployment = kube("deployment", "housing")
    spec = deployment["spec"]
    assert spec["replicas"] >= 1
    assert (
        deployment["status"].get("observedGeneration", 0)
        >= deployment["metadata"]["generation"]
    )
    assert deployment["status"].get("updatedReplicas", 0) == spec["replicas"]
    assert deployment["status"].get("readyReplicas", 0) == spec["replicas"]
    assert spec["template"]["spec"]["containers"][0]["image"] == "housing:v1"
    pods = kube("pods", "-l", "app=housing")["items"]
    assert pods
    assert all(p["status"].get("containerStatuses") for p in pods)
    assert all(
        c["ready"] and c.get("imageID")
        for p in pods
        for c in p["status"]["containerStatuses"]
    )
    service = kube("service", "housing")
    assert service["spec"]["selector"] == {"app": "housing"}
    slices = kube("endpointslices", "-l", "kubernetes.io/service-name=housing")["items"]
    assert any(
        e.get("conditions", {}).get("ready", True)
        for s in slices
        for e in s.get("endpoints", [])
    )
    status, ready = http("/ready")
    assert status == 200 and ready["model_version"] == expected
    request_path = Path(__file__).resolve().parents[4] / "labs/housing/request.json"
    body = json.loads(request_path.read_text())
    status, prediction = http("/predict", body)
    assert status == 200 and prediction["model_version"] == expected
    assert len(prediction["predictions"]) == len(body["instances"])

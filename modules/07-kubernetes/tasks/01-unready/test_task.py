"""Read the explicitly prepared model-less deployment and direct Pod HTTP."""

import pytest

pytestmark = pytest.mark.integration


def test_model_missing_is_alive_but_not_routable(kube, http):
    deployment = kube("deployment", "housing")
    container = deployment["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == "housing:course"
    assert container["livenessProbe"]["httpGet"]["path"] == "/live"
    assert container["readinessProbe"]["httpGet"]["path"] == "/ready"
    pods = kube("pods", "-l", "app=housing")["items"]
    assert pods, "Prepare the model-less deployment first"
    assert all(p["status"]["phase"] == "Running" for p in pods)
    assert all(p["status"].get("containerStatuses") for p in pods)
    assert all(
        not c["ready"] for p in pods for c in p["status"].get("containerStatuses", [])
    )
    service = kube("service", "housing")
    assert service["spec"]["selector"] == {"app": "housing"}
    slices = kube("endpointslices", "-l", "kubernetes.io/service-name=housing")["items"]
    assert not any(
        e.get("conditions", {}).get("ready", True)
        for s in slices
        for e in s.get("endpoints", [])
    )
    assert http("/live")[0] == 200
    assert http("/ready")[0] == 503

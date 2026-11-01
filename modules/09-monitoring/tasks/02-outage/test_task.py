import json
import os
from urllib.request import urlopen

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("MLOPS_RUN_INTEGRATION") != "1",
        reason="Set MLOPS_RUN_INTEGRATION=1 for the running Prometheus lab",
    ),
]


def get(path):
    address = os.getenv("PROMETHEUS_URL", "http://127.0.0.1:9090")
    try:
        with urlopen(address.rstrip("/") + path, timeout=5) as response:
            return json.load(response)
    except Exception:
        pytest.fail(
            "Prometheus request failed: start labs/monitoring and check PROMETHEUS_URL",
            pytrace=False,
        )


def test_current_target_and_alert_rules():
    data = get("/api/v1/query?query=up%7Bjob%3D%22housing%22%7D")
    assert data.get("status") == "success"
    values = data["data"]["result"]
    assert values, "No housing target: check Prometheus scrape config and /targets"
    expected = os.getenv("MLOPS_EXPECT_UP", "1")
    assert expected in {"0", "1"}, "MLOPS_EXPECT_UP must be 0 or 1"
    assert all(row["value"][1] == expected for row in values), (
        "Target differs from MLOPS_EXPECT_UP; inspect /targets"
    )
    rules = get("/api/v1/rules")["data"]["groups"]
    alerts = [r for g in rules for r in g["rules"] if r.get("type") == "alerting"]
    assert any(r["name"] == "HousingTargetDown" for r in alerts), (
        "Load HousingTargetDown into the running Prometheus"
    )
    assert any(r["name"] != "HousingTargetDown" for r in alerts), (
        "Load your model-readiness or predict-5xx alert"
    )

"""Checks student measurements against a live tabular API and Prometheus."""

import json
import os
import time
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pytest
from course_tasks import course_root, load_solution

s = load_solution(__file__)
pytestmark = [
    pytest.mark.integration,
    pytest.mark.writes,
    pytest.mark.skipif(
        os.getenv("MLOPS_RUN_INTEGRATION") != "1"
        or os.getenv("MLOPS_RUN_WRITES") != "1",
        reason="Enable both flags for real predict traffic and metric increments",
    ),
]


def test_student_load_is_visible_in_prometheus():
    api = os.environ.get("HOUSING_URL", "http://127.0.0.1:8000").rstrip("/")
    prometheus = os.environ.get("PROMETHEUS_URL", "http://127.0.0.1:9090").rstrip("/")
    query = 'sum(http_requests_total{route="/predict"})'

    def total():
        with urlopen(
            prometheus + "/api/v1/query?" + urlencode({"query": query}), timeout=5
        ) as response:
            result = json.load(response)
        assert result["status"] == "success"
        rows = result["data"]["result"]
        return float(rows[0]["value"][1]) if rows else 0.0

    with urlopen(api + "/ready", timeout=5) as response:
        assert response.status == 200
    before = total()
    payload = json.loads((course_root() / "labs/housing/request.json").read_text())
    measured = s.measure_load(api + "/predict", payload, requests=24, concurrency=2)
    assert measured["requests"] == 24 and measured["concurrency"] == 2
    assert measured["status_counts"] == {"200": 24}
    durations = np.asarray(measured["durations_seconds"])
    assert durations.shape == (24,) and np.isfinite(durations).all()
    assert (durations >= 0).all() and measured["seconds"] > 0
    assert measured["p95_seconds"] == pytest.approx(float(np.percentile(durations, 95)))
    summary = s.summarize_run(measured)
    assert summary["rps"] == pytest.approx(24 / measured["seconds"])
    assert summary["error_ratio"] == 0
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        if total() >= before + 24:
            break
        time.sleep(0.5)
    else:
        pytest.fail(
            "Prometheus did not scrape the generated predict traffic; inspect target and metric labels"
        )

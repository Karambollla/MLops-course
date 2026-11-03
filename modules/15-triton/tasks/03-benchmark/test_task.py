import json
import os
from types import SimpleNamespace
from unittest.mock import Mock

from housing.features import FEATURES

import pytest
from course_tasks import load_solution, load_task

s = load_solution(__file__)


def test_wall_clock_throughput_and_percentiles():
    rows = [
        {"latency_ms": value, "status": status}
        for value, status in [(10, 200), (20, 500), (30, 200)]
    ]
    result = s.latency_summary(rows, 1.0, min_requests=3)
    assert result["p50_ms"] == 20
    assert result["p95_ms"] == pytest.approx(29)
    assert result["throughput_rps"] == 3
    assert result["error_ratio"] == pytest.approx(1 / 3)


def test_insufficient_and_nonfinite_measurements_do_not_form_a_benchmark():
    with pytest.raises(ValueError):
        s.latency_summary([{"latency_ms": 10, "status": 200}], 1)
    with pytest.raises(ValueError):
        s.latency_summary(
            [{"latency_ms": float("nan"), "status": 200}], 1, min_requests=1
        )
    with pytest.raises(ValueError):
        s.latency_summary([{"latency_ms": 10, "status": 200}], 0, min_requests=1)


def test_default_minimum_request_count_boundary():
    rows = [{"latency_ms": 0, "status": 200}] * 200
    with pytest.raises(ValueError):
        s.latency_summary(rows[:-1], 2)
    assert s.latency_summary(rows, 2) == {
        "p50_ms": 0,
        "p95_ms": 0,
        "throughput_rps": 100,
        "error_ratio": 0,
    }


def test_linear_percentiles_and_http_error_boundary_use_all_rows():
    rows = [
        {"latency_ms": latency, "status": status}
        for latency, status in [(100, 500), (0, 200), (20, 400), (10, 399)]
    ]
    result = s.latency_summary(rows, 2, min_requests=4)
    assert result == pytest.approx(
        {
            "p50_ms": 15,
            "p95_ms": 88,
            "throughput_rps": 2,
            "error_ratio": 0.5,
        }
    )
    assert s.latency_summary(rows, 4, min_requests=4)["throughput_rps"] == 1


@pytest.mark.parametrize("elapsed", [-1, float("nan"), float("inf")])
def test_invalid_wall_time(elapsed):
    with pytest.raises(ValueError):
        s.latency_summary([{"latency_ms": 1, "status": 200}], elapsed, min_requests=1)


@pytest.mark.parametrize("latency", [-1, float("inf"), -float("inf")])
def test_invalid_latency(latency):
    with pytest.raises(ValueError):
        s.latency_summary([{"latency_ms": latency, "status": 200}], 1, min_requests=1)


def test_benchmark_measures_student_infer_and_excludes_warmup(monkeypatch):
    clock = {"now": 0.0}

    def measured_call(*args, **kwargs):
        clock["now"] += 0.02
        return {"variable": [[1.0]]}

    call = Mock(side_effect=measured_call)
    monkeypatch.setattr(s, "load_task", lambda task: SimpleNamespace(infer=call))
    monkeypatch.setattr(s, "perf_counter", lambda: clock["now"])
    result = s.benchmark(object(), [{"a": 1}], ["a"], requests=3, warmup=2)
    assert call.call_count == 5
    assert set(result) == {"rows", "elapsed_seconds"}
    assert len(result["rows"]) == 3
    assert result["elapsed_seconds"] == pytest.approx(0.06)
    assert all(
        row["status"] == 200 and row["latency_ms"] == pytest.approx(20)
        for row in result["rows"]
    )
    assert (
        s.latency_summary(result["rows"], result["elapsed_seconds"], min_requests=3)[
            "error_ratio"
        ]
        == 0
    )


def test_benchmark_records_failed_measured_requests_without_error_text(monkeypatch):
    call = Mock(side_effect=[{}, TimeoutError("private-server-response"), {}])
    monkeypatch.setattr(s, "load_task", lambda task: SimpleNamespace(infer=call))
    result = s.benchmark(object(), [{"a": 1}], ["a"], requests=3, warmup=0)
    assert len(result["rows"]) == 3 and call.call_count == 3
    assert [row["status"] for row in result["rows"]] == [200, 500, 200]
    assert "private-server-response" not in json.dumps(result)
    assert s.latency_summary(result["rows"], result["elapsed_seconds"], min_requests=3)[
        "error_ratio"
    ] == pytest.approx(1 / 3)


@pytest.mark.parametrize(
    "requests,warmup", [(0, 0), (-1, 0), (1, -1), (True, 0), (1.5, 0), (1, 0.5)]
)
def test_benchmark_rejects_invalid_counts_before_network(requests, warmup):
    with pytest.raises(ValueError):
        s.benchmark(None, [{"a": 1}], ["a"], requests=requests, warmup=warmup)


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1",
    reason="Existing compatible Triton server opt-in",
)
def test_live_benchmark_uses_real_student_client():
    server = load_task("15-triton/02-server")
    row = dict(zip(FEATURES, [8.3, 41, 6.9, 1, 322, 2.5, 37.8, -122.2]))
    with server.create_client(
        os.getenv("TRITON_URL", "http://127.0.0.1:8000")
    ) as client:
        assert client.is_server_ready() and client.is_model_ready("housing")
        measured = s.benchmark(client, [row], list(FEATURES), requests=3, warmup=1)
    assert len(measured["rows"]) == 3
    assert all(
        item["status"] == 200 and item["latency_ms"] >= 0 for item in measured["rows"]
    )
    assert measured["elapsed_seconds"] > 0
    summary = s.latency_summary(
        measured["rows"], measured["elapsed_seconds"], min_requests=3
    )
    assert summary["error_ratio"] == 0
    assert summary["throughput_rps"] > 0

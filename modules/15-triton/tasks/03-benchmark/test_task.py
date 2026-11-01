import pytest
from course_tasks import load_solution

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

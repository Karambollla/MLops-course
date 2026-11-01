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

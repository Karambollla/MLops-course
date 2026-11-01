import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_ttft_uses_content_not_the_first_network_chunk():
    result = s.request_metrics(
        0.9, [{"time": 1.0, "content": ""}, {"time": 1.15, "content": "hello"}], 1.5, 4
    )
    assert result["ttft_ms"] == pytest.approx(250)
    assert result["total_ms"] == pytest.approx(600)
    assert result["output_tokens"] == 4
    assert result["tpot_ms"] == pytest.approx(350 / 3)
    assert s.request_metrics(0, [{"time": 1, "content": "x"}], 1, 1)["tpot_ms"] is None


def test_missing_content_and_reversed_times_are_errors():
    with pytest.raises(ValueError):
        s.request_metrics(0, [{"time": 1, "content": ""}], 2, 1)
    with pytest.raises(ValueError):
        s.request_metrics(2, [{"time": 1, "content": "x"}], 3, 1)
    with pytest.raises(ValueError):
        s.request_metrics(0, [{"time": 1, "content": "x"}], 2, 0)

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


def test_multiple_content_events_do_not_replace_output_token_count():
    result = s.request_metrics(
        10,
        [
            {"time": 10.1, "content": ""},
            {"time": 10.2, "content": "several words in one chunk"},
            {"time": 10.4, "content": "last"},
        ],
        11,
        9,
    )
    assert result == pytest.approx(
        {
            "ttft_ms": 200,
            "total_ms": 1000,
            "output_tokens": 9,
            "tpot_ms": 100,
        }
    )


@pytest.mark.parametrize(
    "started,events,ended",
    [
        (0, [{"time": -0.1, "content": ""}, {"time": 0.5, "content": "x"}], 1),
        (0, [{"time": 0.5, "content": "x"}, {"time": 1.1, "content": ""}], 1),
        (0, [{"time": 0.7, "content": "x"}, {"time": 0.6, "content": "y"}], 1),
        (2, [{"time": 2, "content": "x"}], 1),
    ],
)
def test_all_event_times_must_be_ordered_and_inside_request(started, events, ended):
    with pytest.raises(ValueError):
        s.request_metrics(started, events, ended, 4)

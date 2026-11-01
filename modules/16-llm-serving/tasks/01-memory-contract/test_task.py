import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_weight_and_gqa_cache_sizes_are_in_bytes():
    assert s.weights_bytes(500_000_000) == 1_000_000_000
    assert s.weights_bytes(7_000_000_000) == 14_000_000_000
    assert s.kv_cache_bytes(24, 8, 64, 2048, 1) == 100_663_296
    assert s.kv_cache_bytes(24, 8, 64, 2048, 8) == 805_306_368


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_memory_estimate_rejects_invalid_sizes(value):
    with pytest.raises(ValueError):
        s.weights_bytes(value)


def test_sse_ignores_metadata_and_stops_at_done():
    events = [
        ": heartbeat",
        'data: {"choices":[{"delta":{"role":"assistant"}}]}',
        "",
        'data: {"choices":[{"delta":{"content":"Hel"}}]}',
        'data: {"choices":[{"delta":{"content":"lo"}}]}',
        "data: [DONE]",
        "data: {broken",
    ]
    assert s.sse_contents(events) == ["Hel", "lo"]
    with pytest.raises(ValueError):
        s.sse_contents(['data: {"error":{"message":"context too long"}}'])
    with pytest.raises(ValueError):
        s.sse_contents(["data: {broken"])


@pytest.mark.parametrize("position", range(6))
@pytest.mark.parametrize("invalid", [0, -1, True, 1.5])
def test_kv_cache_rejects_invalid_dimensions(position, invalid):
    args = [24, 8, 64, 2048, 1, 2]
    args[position] = invalid
    with pytest.raises(ValueError):
        s.kv_cache_bytes(*args)


@pytest.mark.parametrize("invalid", [0, -1, True, 1.5])
def test_weight_bytes_per_parameter_is_validated(invalid):
    with pytest.raises(ValueError):
        s.weights_bytes(10, invalid)


def test_weights_respect_nondefault_bytes_per_parameter():
    assert s.weights_bytes(17, 1) == 17
    assert s.weights_bytes(17, 4) == 68


def test_sse_returns_all_nonempty_choices_in_event_order():
    lines = [
        'data: {"choices":[{"delta":{"content":""}},{"delta":{"content":"two words"}}]}',
        ": heartbeat",
        'data: {"choices":[{"delta":{"content":" A"}},{"delta":{"role":"assistant"}},{"delta":{"content":" B"}}]}',
        "data: [DONE]",
        'data: {"error":{"message":"ignored after done"}}',
    ]
    assert s.sse_contents(lines) == ["two words", " A", " B"]
    assert s.sse_contents(["", ": heartbeat", "data: [DONE]"]) == []

import json
from pathlib import Path

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


def test_own_prompt_corpus_is_ready_for_a_reproducible_benchmark():
    prompts = json.loads(Path(__file__).with_name("prompts.json").read_text())
    assert len(prompts) >= 20, "Заполни20 prompts разных длин в prompts.json"
    assert len({p["id"] for p in prompts}) == len(prompts)
    assert all(isinstance(p["text"], str) and p["text"].strip() for p in prompts)

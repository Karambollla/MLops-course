import json
from pathlib import Path

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


def test_submitted_gpu_comparison_has_comparable_inputs():
    report = json.loads(Path(__file__).with_name("benchmark.json").read_text())
    assert isinstance(report["gpu_model"], str) and report["gpu_model"].strip(), (
        "Нужен реальный NVIDIA GPU benchmark, см. README"
    )
    assert set(report["engines"]) == {"vllm", "sglang"}
    for row in report["engines"].values():
        assert (
            row["model_revision"] == report["model_revision"]
            and row["corpus_sha256"] == report["corpus_sha256"]
        )
        assert row["warmup"] >= 20
        assert {int(k) for k in row["concurrency"]} == {1, 4}
        assert all(
            v["requests"] >= 100 and 0 <= v["errors"] <= v["requests"]
            for v in row["concurrency"].values()
        )

import json
import re
from pathlib import Path


def test_engine_metadata_and_observed_inference_are_recorded():
    report = json.loads(Path(__file__).with_name("engine-report.json").read_text())
    assert report["release"] == "25.06", "Заполни отчёт совместимого NVIDIA-стенда"
    for key in ["model_id", "model_revision", "gpu_model", "driver"]:
        assert isinstance(report[key], str) and report[key].strip(), f"Нет {key}"
    assert re.fullmatch(r"[0-9a-f]{64}", report["engine_sha256"] or "")
    assert report["backend"] == "tensorrtllm"
    assert report["model_supported_by_release"] is True
    assert report["commands"] and all(
        isinstance(cmd, str) and cmd.strip() for cmd in report["commands"]
    )
    assert report["inference"]["status"] == 200
    assert report["inference"]["output_tokens"] > 0
    assert report["inference"]["model_revision"] == report["model_revision"]

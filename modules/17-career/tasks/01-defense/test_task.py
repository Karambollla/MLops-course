import json
from pathlib import Path


def test_defense_plan_has_recording_ordered_sections_and_real_checks():
    report = json.loads(Path(__file__).with_name("defense.json").read_text())
    assert isinstance(report["recording"], str) and report["recording"].strip(), (
        "Добавь путь к собственной записи/URL"
    )
    assert (
        isinstance(report["duration_seconds"], (int, float))
        and report["duration_seconds"] > 0
    )
    sections = report["sections"]
    assert {s["topic"] for s in sections} >= {
        "task",
        "data_metrics",
        "release",
        "incident",
        "limits",
    }
    assert all(
        0 <= s["start_seconds"] < s["end_seconds"] <= report["duration_seconds"]
        for s in sections
    )
    assert all(
        a["end_seconds"] <= b["start_seconds"] for a, b in zip(sections, sections[1:])
    )
    assert report["checks"]["predict_status"] == 200
    assert report["checks"]["rollback_verified"] is True
    assert (
        isinstance(report["checks"]["model_version"], str)
        and report["checks"]["model_version"].strip()
    )
    assert report["independent_reproduction"]["exit_code"] == 0
    assert report["independent_reproduction"]["reviewer"]

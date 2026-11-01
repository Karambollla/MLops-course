import json
from pathlib import Path


def test_three_real_runs_are_consistent_with_change_notifications():
    report = json.loads(Path(__file__).with_name("report.json").read_text())
    runs = report["runs"]
    assert len(runs) == 3, "Запиши три запуска в report.json"
    assert [r["workers"] for r in runs] == [1, 2, 2]
    assert all(r["failed"] == 0 and r["unreachable"] == 0 for r in runs)
    assert runs[1]["changed"] > 0 and runs[1]["handlers"], (
        "Изменение шаблона должно вызвать handler"
    )
    assert runs[2]["changed"] == 0 and runs[2]["handlers"] == []
    assert runs[1]["config_sha256"] == runs[2]["config_sha256"]
    assert runs[0]["config_sha256"] != runs[1]["config_sha256"]
    assert report["invalid_workers_rejected"] is True

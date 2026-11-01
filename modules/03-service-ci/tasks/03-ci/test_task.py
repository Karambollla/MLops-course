"""Свидетельства CI проверяем напрямую, без обязательного student grader."""

from pathlib import Path

from course_tasks import read_json


def test_actual_ci_red_then_green():
    runs = read_json(Path(__file__).parent / "ci-runs.json")
    assert len(runs) >= 2, "Запиши реальные красный и зелёный runs"
    red = [r for r in runs if r["conclusion"] == "failure"]
    green = [r for r in runs if r["conclusion"] == "success"]
    assert red and green
    selected = green[-1]
    assert {"tests", "structure"} <= set(selected["passed_checks"])
    previous = [
        r
        for r in red
        if r["branch"] == selected["branch"]
        and r["sha"] != selected["sha"]
        and r["run_number"] < selected["run_number"]
    ]
    assert previous, "Красный и зелёный run должны быть одной ветки, red раньше green"
    for run in [previous[-1], selected]:
        assert isinstance(run["sha"], str) and len(run["sha"]) == 40
        assert (
            run["url"].startswith("https://github.com/")
            and "/actions/runs/" in run["url"]
        )
        assert run["branch"] and run["branch"] not in ["main", "master"], (
            "Намеренный сбой делай в отдельной ветке"
        )

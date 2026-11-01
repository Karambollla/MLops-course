"""Офлайн-контракты; синтетические fixtures не являются доказательством запуска."""

import json
from pathlib import Path

import pytest
from course_tasks import load_solution

solution = load_solution(__file__)
grading = load_solution(__file__, filename="grading.py")


def sample():
    return json.loads(Path(__file__).with_name("scenario.json").read_text())


def test_valid_observations():
    assert grading.validate_report(sample())["runs"][0] == {
        "rps": 20.0,
        "error_ratio": 0.05,
        "p95_seconds": 0.08,
    }


def test_reject_inconsistent_0():
    report = sample()
    report["runs"][0]["status_counts"]["200"] = 1
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_1():
    report = sample()
    report["datasource"] = "http://localhost:9090"
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_zero_traffic_is_unknown():
    assert solution.summarize_run(
        {
            "concurrency": 1,
            "requests": 0,
            "seconds": 2,
            "status_counts": {},
            "p95_seconds": None,
        }
    ) == {"rps": 0, "error_ratio": None, "p95_seconds": None}


def test_client_errors_are_not_server_errors():
    result = solution.summarize_run(
        {
            "concurrency": 1,
            "requests": 10,
            "seconds": 2,
            "status_counts": {"400": 8, "500": 2},
            "p95_seconds": 0.2,
        }
    )
    assert result["error_ratio"] == pytest.approx(0.2)


def test_own_observations_are_complete_and_consistent():
    report = json.loads(Path(__file__).with_name("report.json").read_text())
    grading.validate_report(report)

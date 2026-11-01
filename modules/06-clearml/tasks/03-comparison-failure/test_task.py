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
    assert grading.validate_report(sample()) == {
        "level": "offline",
        "detection_seconds": 1,
    }


def test_reject_inconsistent_0():
    report = sample()
    report["clearml_mae"] = 99
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_1():
    report = sample()
    report["failure"]["recovered_at"] = 0
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_2():
    report = sample()
    report["failure"]["queue_tested"] = True
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_3():
    report = sample()
    report["parameters_equal"] = False
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_own_observations_are_complete_and_consistent():
    report = json.loads(Path(__file__).with_name("report.json").read_text())
    grading.validate_report(report)

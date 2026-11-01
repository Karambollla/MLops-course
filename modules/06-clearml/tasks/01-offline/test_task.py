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
    assert grading.validate_report(sample()) == {"mode": "offline", "mae": 0.42}


def test_reject_inconsistent_0():
    report = sample()
    report["metrics"]["mae"] = float("nan")
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_1():
    report = sample()
    report["data_sha256"] = "unknown"
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_2():
    report = sample()
    report["artifacts"] = ["metrics.json"]
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_3():
    report = sample()
    report["metrics"]["rmse"] = 0.1
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_training_is_student_implementation():
    class RecordingTask:
        def __init__(self):
            self.parameters = None

        def connect(self, values):
            self.parameters = values

    # Запуск обязан вернуть измерения, а не константу-пример из теории.
    report = solution.train_and_log(RecordingTask())
    assert report["train_exit_code"] == 0
    assert report["metrics"]["mae"] >= 0


def test_own_observations_are_complete_and_consistent():
    report = json.loads(Path(__file__).with_name("report.json").read_text())
    grading.validate_report(report)

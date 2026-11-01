"""Офлайн-контракты; синтетические fixtures не являются доказательством запуска."""

import json
from pathlib import Path

import pytest
from course_tasks import load_solution

solution = load_solution(__file__)
grading = load_solution(__file__, filename="grading.py")


def sample():
    return json.loads(Path(__file__).with_name("scenario.json").read_text())


def test_join_by_id_and_quantiles():
    result = grading.validate_report(sample())
    assert result["mae"] == pytest.approx(2 / 3)
    assert result["reference_quantiles"] == pytest.approx([1.4, 3, 4.6])
    assert result["shifted_quantiles"] == pytest.approx([3.4, 5, 6.6])
    assert result["median_shift"] == 2


def test_reject_inconsistent_0():
    report = sample()
    report["predictions"][0]["id"] = "missing"
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_1():
    report = sample()
    report["predictions"][0]["id"] = "a"
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_2():
    report = sample()
    report["reference_medinc"] = []
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_3():
    report = sample()
    report["targets"][0]["target"] = float("nan")
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_own_observations_are_complete_and_consistent():
    report = json.loads(Path(__file__).with_name("report.json").read_text())
    grading.validate_report(report)

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
    assert grading.validate_report(sample()) == {"expired": True, "revoked": True}


def test_reject_inconsistent_0():
    report = sample()
    report["after_at"] = 150
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_1():
    report = sample()
    report["after_status"] = 200
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_2():
    report = sample()
    report["max_attempts"] = 100
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_3():
    report = sample()
    report["renewable_trial"]["read_after_revoke"] = 200
    with pytest.raises(ValueError):
        grading.validate_report(report)


@pytest.mark.parametrize(
    "status,timeout,expected",
    [
        (403, False, "access_denied"),
        (None, True, "network_timeout"),
        (200, False, "ok"),
        (500, False, "http_error"),
    ],
)
def test_error_classification(status, timeout, expected):
    assert solution.classify_error(status, timeout) == expected


def test_own_observations_are_complete_and_consistent():
    report = json.loads(Path(__file__).with_name("report.json").read_text())
    grading.validate_report(report)

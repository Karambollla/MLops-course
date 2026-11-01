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
        "model_version": "housing-run-42",
        "ready": True,
    }


def test_reject_inconsistent_0():
    report = sample()
    report["model_version"] = "wrong-run"
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_1():
    report = sample()
    report["service_ready_endpoints"] = 0
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_2():
    report = sample()
    report["pod_config_revision"] = "1"
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_3():
    report = sample()
    report["memory_request_mib"] = 2048
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_own_observations_are_complete_and_consistent():
    report = json.loads(Path(__file__).with_name("report.json").read_text())
    grading.validate_report(report)

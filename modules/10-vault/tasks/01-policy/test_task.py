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
    assert grading.validate_report(sample()) == {"least_privilege": True}


def test_reject_inconsistent_0():
    report = sample()
    report["neighbor_status"] = 200
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_1():
    report = sample()
    report["write_status"] = 200
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_2():
    report = sample()
    report["token_role"] = "root"
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_reject_inconsistent_3():
    report = sample()
    report["secret_logged"] = True
    with pytest.raises(ValueError):
        grading.validate_report(report)


def test_secret_never_returned():
    result = solution.inspect_payload(
        {"data": {"data": {"artifact_key": "private-demo"}, "metadata": {"version": 1}}}
    )
    assert result == {"field_present": True}
    assert "private-demo" not in json.dumps(result)


def test_missing_key_rejected():
    with pytest.raises(ValueError):
        solution.inspect_payload({"data": {"data": {}}})


def test_own_observations_are_complete_and_consistent():
    report = json.loads(Path(__file__).with_name("report.json").read_text())
    grading.validate_report(report)

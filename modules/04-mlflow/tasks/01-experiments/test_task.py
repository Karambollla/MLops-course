"""Offline проверки поведения; исходная заготовка должна быть RED."""

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def runs():
    return [
        {
            "run_id": str(i),
            "status": "FINISHED",
            "parameters": {"alpha": i},
            "data_sha256": "a" * 64,
            "split": {"train": [0], "validation": [1], "test": [2]},
            "validation_mae": m,
            "validation_rmse": m + 0.1,
            "test_mae": 10 - i,
        }
        for i, m in enumerate([0.8, 0.5, 0.6])
    ]


def test_validation_selects_not_test():
    r = runs()
    assert s.select_candidate(r) == "1"
    r[0]["test_mae"] = 0.0
    assert s.select_candidate(r) == "1"


@pytest.mark.parametrize(
    "mutation", ["hash", "split", "status", "nan", "duplicate", "count"]
)
def test_incomparable_experiments(mutation):
    r = runs()
    if mutation == "hash":
        r[1]["data_sha256"] = "b" * 64
    if mutation == "split":
        r[1]["split"]["test"] = [3]
    if mutation == "status":
        r[1]["status"] = "FAILED"
    if mutation == "nan":
        r[1]["validation_mae"] = float("nan")
    if mutation == "duplicate":
        r[1]["parameters"] = r[0]["parameters"]
    if mutation == "count":
        r = r[:2]
    with pytest.raises(ValueError):
        s.select_candidate(r)

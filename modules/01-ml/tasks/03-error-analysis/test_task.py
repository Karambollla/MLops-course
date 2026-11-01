"""Offline проверки поведения; исходная заготовка должна быть RED."""

import pandas as pd
import pytest
import numpy as np
from course_tasks import load_solution

s = load_solution(__file__)


def test_quartiles_and_counts():
    rows = s.quartile_errors(list(range(8)), [0] * 8)
    assert [r["quartile"] for r in rows] == [1, 2, 3, 4]
    assert [r["count"] for r in rows] == [2] * 4
    assert [r["mae"] for r in rows] == [0.5, 2.5, 4.5, 6.5]
    assert [r["rmse"] for r in rows] == pytest.approx(
        [(0.5) ** 0.5, (6.5) ** 0.5, (20.5) ** 0.5, (42.5) ** 0.5]
    )
    assert s.quartile_errors([2, 2], [1, 3]) == [
        {"quartile": 1, "count": 2, "mae": 1.0, "rmse": 1.0}
    ]


def test_geographic_boundary_and_validation():
    f = pd.DataFrame({"Latitude": [33.0, 35.0, 36.0]}, index=[10, 20, 30])
    assert s.geographic_split(f, 35.0) == {"train": [10], "test": [20, 30]}
    with pytest.raises(ValueError):
        s.geographic_split(f, 40.0)
    with pytest.raises(ValueError):
        s.quartile_errors([1, 2], [1])


@pytest.mark.parametrize(
    "truth,predicted,groups",
    [
        ([0, 1, 2, 3, 4, 5, 6], [2, 1, 0, 4, 8, 3, 9], [[0, 1], [2, 3], [4], [5, 6]]),
        (
            [0, 0, 0, 1, 2, 3, 3, 3],
            [1, 2, 3, 1, 0, 4, 5, 6],
            [[0, 1, 2, 3], [4, 5, 6, 7]],
        ),
    ],
)
def test_quartile_metrics_uneven_groups_and_ties(truth, predicted, groups):
    result = s.quartile_errors(truth, predicted)
    assert len(result) == len(groups)
    for quartile, (row, positions) in enumerate(zip(result, groups), start=1):
        errors = np.asarray(truth)[positions] - np.asarray(predicted)[positions]
        assert row == {
            "quartile": quartile,
            "count": len(positions),
            "mae": pytest.approx(np.abs(errors).mean()),
            "rmse": pytest.approx(np.sqrt(np.square(errors).mean())),
        }


@pytest.mark.parametrize(
    "truth,predicted",
    [
        ([], []),
        ([[1]], [[1]]),
        ([float("inf")], [1]),
        ([1], [float("nan")]),
        ([1, 2], [1]),
    ],
)
def test_quartiles_reject_invalid_arrays(truth, predicted):
    with pytest.raises(ValueError):
        s.quartile_errors(truth, predicted)


def test_geographic_order_and_both_empty_sides():
    frame = pd.DataFrame(
        {"Latitude": [35.0, 34.9, 35.1, 30.0]}, index=["d", "a", "c", "b"]
    )
    assert s.geographic_split(frame, 35.0) == {"train": ["a", "b"], "test": ["d", "c"]}
    for cutoff in [30.0, 36.0]:
        with pytest.raises(ValueError):
            s.geographic_split(frame, cutoff)

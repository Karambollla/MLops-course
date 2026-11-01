"""Offline проверки поведения; исходная заготовка должна быть RED."""

import pandas as pd
import pytest
import numpy as np
from course_tasks import load_solution
from housing.features import FEATURES, TARGET
from sklearn.model_selection import train_test_split

s = load_solution(__file__)


def test_metrics():
    assert s.regression_metrics([0, 2], [0, 0]) == {
        "mae": 1.0,
        "rmse": pytest.approx(2**0.5),
    }
    assert s.regression_metrics([1, 1], [1, 1]) == {"mae": 0.0, "rmse": 0.0}


@pytest.mark.parametrize(
    "a,b",
    [
        ([], []),
        ([1], [1, 2]),
        ([float("nan")], [0]),
        ([[1]], [[1]]),
        ([0], [float("inf")]),
    ],
)
def test_invalid_metrics(a, b):
    with pytest.raises(ValueError):
        s.regression_metrics(a, b)


def test_split_exact_and_deterministic():
    part = s.make_split(100, 42)
    trainval, test = train_test_split(list(range(100)), test_size=0.2, random_state=42)
    train, valid = train_test_split(trainval, test_size=0.25, random_state=42)
    assert part == {"train": list(train), "validation": list(valid), "test": list(test)}
    assert part == s.make_split(100, 42)


def test_baseline_uses_train_only():
    f = pd.DataFrame({name: [1.0, 2.0, 3.0, 4.0, 5.0] for name in FEATURES})
    f[TARGET] = [1.0, 3.0, 100.0, 20.0, 40.0]
    p = {"train": [0, 1], "validation": [2], "test": [3, 4]}
    result = s.fit_baseline(f, p)
    assert result["validation"]["mae"] == 98.0
    assert result["test"]["mae"] == 28.0
    with pytest.raises(ValueError):
        s.fit_baseline(f.assign(unexpected=1), p)


@pytest.mark.parametrize(
    "truth,predicted",
    [([1, -2, 8], [4, -2, 0]), ([0.5], [-1.25]), ([3, 5, 9, -2], [1] * 4)],
)
def test_metrics_varied_values(truth, predicted):
    errors = np.asarray(truth) - np.asarray(predicted)
    assert s.regression_metrics(truth, predicted) == {
        "mae": pytest.approx(np.abs(errors).mean()),
        "rmse": pytest.approx(np.sqrt(np.square(errors).mean())),
    }


@pytest.mark.parametrize(
    "bad", [[float("nan")], [float("inf")], [-float("inf")], [[1, 2]], [[[1]]], 1.0]
)
@pytest.mark.parametrize("side", [0, 1])
def test_metrics_reject_invalid_on_either_side(bad, side):
    args = [[0], [0]]
    args[side] = bad
    with pytest.raises(ValueError):
        s.regression_metrics(*args)


@pytest.mark.parametrize("n,seed", [(5, 0), (7, 17), (11, 42), (23, 9), (101, 3)])
def test_split_rounding_and_seeds(n, seed):
    trainval, test = train_test_split(list(range(n)), test_size=0.2, random_state=seed)
    train, valid = train_test_split(trainval, test_size=0.25, random_state=seed)
    expected = {"train": list(train), "validation": list(valid), "test": list(test)}
    assert s.make_split(n, seed) == expected
    assert s.make_split(n, seed) == expected


def test_baseline_uses_positions_and_asymmetric_train_mean():
    frame = pd.DataFrame(
        {name: list(range(6)) for name in FEATURES}, index=[90, 10, 80, 20, 70, 30]
    )
    frame[TARGET] = [1.0, 2.0, 9.0, 100.0, 20.0, 40.0]
    split = {"train": [0, 1, 2], "validation": [3], "test": [4, 5]}
    result = s.fit_baseline(frame, split)
    assert result["validation"] == {"mae": 96.0, "rmse": 96.0}
    assert result["test"] == {"mae": 26.0, "rmse": pytest.approx(776**0.5)}
    for column in FEATURES + [TARGET]:
        with pytest.raises(ValueError):
            s.fit_baseline(frame.drop(columns=column), split)

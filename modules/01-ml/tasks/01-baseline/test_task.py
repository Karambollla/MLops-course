"""Offline проверки поведения; исходная заготовка должна быть RED."""

import pandas as pd
import pytest
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

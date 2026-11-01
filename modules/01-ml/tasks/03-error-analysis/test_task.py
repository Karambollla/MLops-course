"""Offline проверки поведения; исходная заготовка должна быть RED."""

import pandas as pd
import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_quartiles_and_counts():
    rows = s.quartile_errors(list(range(8)), [0] * 8)
    assert [r["quartile"] for r in rows] == [1, 2, 3, 4]
    assert [r["count"] for r in rows] == [2] * 4
    assert [r["mae"] for r in rows] == [0.5, 2.5, 4.5, 6.5]
    assert rows[-1]["rmse"] == pytest.approx((85 / 2) ** 0.5)
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

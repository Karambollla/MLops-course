"""Offline проверки поведения; исходная заготовка должна быть RED."""

import pandas as pd
from course_tasks import load_solution

s = load_solution(__file__)


def test_table_summary(tmp_path):
    f = pd.DataFrame(
        {"x": [1.0, 2.0, 3.0, float("nan")], "label": ["a", "b", None, "c"]}
    )
    r = s.describe_frame(f)
    assert r["shape"] == [4, 2]
    assert r["dtypes"]["x"] == "float64"
    assert r["missing"] == {"x": 1, "label": 1}
    assert r["quantiles"]["x"] == {"0.25": 1.5, "0.5": 2.0, "0.75": 2.5}
    csv = tmp_path / "data.csv"
    f.to_csv(csv, index=False)
    out = tmp_path / "summary.md"
    s.write_report(csv, out)
    assert all(term in out.read_text() for term in ["x", "label", "float64", "0.25"])


def test_alignment_uses_labels():
    left = pd.Series([20, 10, 30], index=["b", "a", "c"])
    right = pd.Series([2, 1, 9], index=["b", "a", "d"])
    a, b = s.align_series(left, right)
    assert list(a.index) == list(b.index) == ["b", "a"]
    assert (a + b).tolist() == [22, 11]

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


def test_multiple_numeric_columns_without_missing_values():
    frame = pd.DataFrame(
        {"a": [0, 2, 4, 10], "b": [10.0, 20.0, 40.0, 80.0], "text": ["x"] * 4}
    )
    result = s.describe_frame(frame)
    assert result["shape"] == [4, 3]
    assert result["dtypes"] == {"a": "int64", "b": "float64", "text": "object"}
    assert result["missing"] == {"a": 0, "b": 0, "text": 0}
    assert result["quantiles"] == {
        "a": {"0.25": 1.5, "0.5": 3.0, "0.75": 5.5},
        "b": {"0.25": 17.5, "0.5": 30.0, "0.75": 50.0},
    }
    assert s.describe_frame(frame[["text"]])["quantiles"] == {}


def test_report_creates_nested_parent(tmp_path):
    csv = tmp_path / "input.csv"
    pd.DataFrame({"amount": [2, 6, 10]}).to_csv(csv, index=False)
    output = tmp_path / "new" / "nested" / "report.md"
    s.write_report(csv, output)
    assert all(term in output.read_text() for term in ["amount", "int64", "0.25"])


def test_alignment_preserves_left_order_and_values():
    left = pd.Series([30, 10, 20], index=["c", "a", "b"])
    right = pd.Series([2, 3, 9], index=["b", "c", "d"])
    a, b = s.align_series(left, right)
    assert list(a.index) == list(b.index) == ["c", "b"]
    assert a.tolist() == [30, 20]
    assert b.tolist() == [3, 2]
    a, b = s.align_series(left, pd.Series([1], index=["z"]))
    assert a.empty and b.empty

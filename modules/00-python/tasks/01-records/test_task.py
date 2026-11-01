"""Offline проверки поведения; исходная заготовка должна быть RED."""

import copy

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_summary_filters_and_does_not_mutate():
    records = [
        {"duration": 2},
        {"duration": 4.0},
        {"duration": True},
        {"duration": -1},
        {"duration": 0},
        {"duration": "3"},
        {},
        {"duration": float("inf")},
        {"duration": float("nan")},
    ]
    before = copy.deepcopy(records)
    assert s.summarize(records) == {"count": 2, "mean": 3.0}
    assert len(records) == len(before)
    for a, b in zip(records, before):
        assert a.keys() == b.keys()
        for key in a:
            assert a[key] == b[key] or (
                isinstance(a[key], float) and a[key] != a[key] and b[key] != b[key]
            )


def test_empty_and_no_valid_values():
    assert s.summarize([]) == {"count": 0, "mean": None}
    assert s.summarize([{}, {"duration": False}]) == {"count": 0, "mean": None}


def test_fractional_mean_and_nested_metadata_unchanged():
    records = [
        {"duration": 0.25, "metadata": {"tags": ["a", {"x": 2}]}},
        {"duration": 1.5},
        {"duration": 4},
    ]
    before = copy.deepcopy(records)
    assert s.summarize(records) == {"count": 3, "mean": pytest.approx(5.75 / 3)}
    assert records == before


@pytest.mark.parametrize(
    "value",
    [
        None,
        False,
        True,
        "1",
        [],
        {},
        -3,
        0,
        -0.5,
        float("nan"),
        float("inf"),
        -float("inf"),
    ],
)
def test_each_invalid_duration_is_ignored(value):
    assert s.summarize([{"duration": value}]) == {"count": 0, "mean": None}

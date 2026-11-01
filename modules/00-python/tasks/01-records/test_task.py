"""Offline проверки поведения; исходная заготовка должна быть RED."""

import copy

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

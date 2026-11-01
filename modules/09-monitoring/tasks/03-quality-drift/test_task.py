import json
from pathlib import Path

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def sample():
    return json.loads(Path(__file__).with_name("scenario.json").read_text())


def analyze(p):
    return s.analyze(
        p["targets"], p["predictions"], p["reference_medinc"], p["shifted_medinc"]
    )


def test_join_and_linear_quantiles():
    r = analyze(sample())
    assert r["mae"] == pytest.approx(2 / 3)
    assert r["reference_quantiles"] == pytest.approx([1.4, 3, 4.6])
    assert r["shifted_quantiles"] == pytest.approx([3.4, 5, 6.6])
    assert r["median_shift"] == 2


def test_order_does_not_change_join():
    p = sample()
    p["predictions"].reverse()
    assert analyze(p) == analyze(sample())


@pytest.mark.parametrize("case", ["missing", "duplicate", "empty", "nan"])
def test_invalid_inputs(case):
    p = sample()
    if case == "missing":
        p["predictions"][0]["id"] = "unknown"
    if case == "duplicate":
        p["predictions"][0]["id"] = "a"
    if case == "empty":
        p["reference_medinc"] = []
    if case == "nan":
        p["targets"][0]["target"] = float("nan")
    with pytest.raises(ValueError):
        analyze(p)

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


def test_target_order_does_not_change_join():
    p = sample()
    p["targets"] = p["targets"][1:] + p["targets"][:1]
    assert analyze(p) == analyze(sample())


def test_independent_join_and_unchanged_distribution():
    result = s.analyze(
        [
            {"id": "a", "target": 0},
            {"id": "b", "target": 10},
            {"id": "c", "target": 20},
        ],
        [
            {"id": "c", "prediction": 17},
            {"id": "a", "prediction": 2},
            {"id": "b", "prediction": 11},
        ],
        [1, 5],
        [5, 1],
    )
    assert result["mae"] == pytest.approx(2.0)
    assert result["reference_quantiles"] == pytest.approx([1.4, 3.0, 4.6])
    assert result["shifted_quantiles"] == pytest.approx([1.4, 3.0, 4.6])
    assert result["median_shift"] == pytest.approx(0)


def test_single_observation_has_three_equal_quantiles():
    result = s.analyze(
        [{"id": "only", "target": 3}],
        [{"id": "only", "prediction": 2}],
        [2],
        [9],
    )
    assert result == {
        "mae": 1.0,
        "reference_quantiles": [2.0, 2.0, 2.0],
        "shifted_quantiles": [9.0, 9.0, 9.0],
        "median_shift": 7.0,
    }


@pytest.mark.parametrize("side", ["targets", "predictions"])
@pytest.mark.parametrize("case", ["missing", "duplicate", "extra", "empty"])
def test_both_sides_require_the_same_unambiguous_ids(side, case):
    p = sample()
    if case == "missing":
        p[side].pop()
    elif case == "duplicate":
        p[side][1]["id"] = p[side][0]["id"]
    elif case == "extra":
        p[side].append({**p[side][0], "id": "extra"})
    else:
        p[side] = []
    with pytest.raises(ValueError):
        analyze(p)


@pytest.mark.parametrize(
    "side,field", [("targets", "target"), ("predictions", "prediction")]
)
@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), -float("inf"), "invalid", None]
)
def test_bad_target_or_prediction_is_rejected(side, field, value):
    p = sample()
    p[side][0][field] = value
    with pytest.raises(ValueError):
        analyze(p)


@pytest.mark.parametrize("side", ["reference_medinc", "shifted_medinc"])
@pytest.mark.parametrize(
    "values", [[], [float("nan")], [float("inf")], [-float("inf")], ["invalid"], [None]]
)
def test_both_distributions_require_finite_numeric_samples(side, values):
    p = sample()
    p[side] = values
    with pytest.raises(ValueError):
        analyze(p)

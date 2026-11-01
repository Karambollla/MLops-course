import json
from pathlib import Path

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_measured_load_summaries():
    runs = json.loads(Path(__file__).with_name("scenario.json").read_text())["runs"]
    assert s.summarize_run(runs[0]) == {
        "rps": 20,
        "error_ratio": 0.05,
        "p95_seconds": 0.08,
    }
    assert s.summarize_run(runs[1]) == {"rps": 50, "error_ratio": 0, "p95_seconds": 0.1}


def test_zero_traffic():
    assert s.summarize_run(
        dict(concurrency=1, requests=0, seconds=2, status_counts={}, p95_seconds=None)
    ) == {"rps": 0, "error_ratio": None, "p95_seconds": None}


def test_4xx_are_not_5xx():
    assert (
        s.summarize_run(
            dict(
                concurrency=1,
                requests=10,
                seconds=2,
                status_counts={"400": 8, "500": 2},
                p95_seconds=0.2,
            )
        )["error_ratio"]
        == 0.2
    )


@pytest.mark.parametrize(
    "patch",
    [
        {"seconds": 0},
        {"concurrency": 0},
        {"status_counts": {"200": -1}},
        {"status_counts": {"200": 1}},
        {"p95_seconds": -1},
    ],
)
def test_invalid_measurements(patch):
    run = dict(
        concurrency=1,
        requests=10,
        seconds=2,
        status_counts={"200": 10},
        p95_seconds=0.2,
    )
    run.update(patch)
    with pytest.raises(ValueError):
        s.summarize_run(run)


@pytest.mark.parametrize(
    "counts,seconds,p95,expected",
    [
        ({"200": 2, "201": 1}, 2, 0.125, (1.5, 0.0)),
        ({"500": 2, "503": 1}, 2, 0.25, (1.5, 1.0)),
        ({"200": 4, "400": 2, "499": 1, "500": 2, "599": 1}, 4, 0.2, (2.5, 0.3)),
        ({"200": 1}, 0.4, 0.0, (2.5, 0.0)),
    ],
)
def test_fractional_rps_and_http_error_boundaries(counts, seconds, p95, expected):
    result = s.summarize_run(
        dict(
            concurrency=2,
            requests=sum(counts.values()),
            seconds=seconds,
            status_counts=counts,
            p95_seconds=p95,
        )
    )
    assert set(result) == {"rps", "error_ratio", "p95_seconds"}
    assert result["rps"] == pytest.approx(expected[0])
    assert result["error_ratio"] == pytest.approx(expected[1])
    assert result["p95_seconds"] == p95


def test_zero_counts_are_still_no_traffic():
    result = s.summarize_run(
        dict(
            concurrency=4,
            requests=0,
            seconds=0.5,
            status_counts={"200": 0, "500": 0},
            p95_seconds=None,
        )
    )
    assert result == {"rps": 0, "error_ratio": None, "p95_seconds": None}


@pytest.mark.parametrize("field", ["seconds", "p95_seconds"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_measurements_are_rejected(field, value):
    run = dict(
        concurrency=1,
        requests=2,
        seconds=1.5,
        status_counts={"200": 2},
        p95_seconds=0.2,
    )
    run[field] = value
    with pytest.raises(ValueError):
        s.summarize_run(run)


@pytest.mark.parametrize(
    "patch",
    [
        {"seconds": -1},
        {"concurrency": -1},
        {"status_counts": {"200": 9.5, "500": 0.5}},
        {"status_counts": {"200": 11}},
    ],
)
def test_invalid_counts_and_negative_measurements(patch):
    run = dict(
        concurrency=1,
        requests=10,
        seconds=2,
        status_counts={"200": 10},
        p95_seconds=0.2,
    )
    run.update(patch)
    with pytest.raises(ValueError):
        s.summarize_run(run)

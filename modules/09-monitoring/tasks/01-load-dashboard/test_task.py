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

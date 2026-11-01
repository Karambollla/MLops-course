"""Offline проверки поведения; исходная заготовка должна быть RED."""

import copy

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_intervals_are_stable_and_utc():
    expected = {
        "data_interval_start": "2025-01-01T00:00:00+00:00",
        "data_interval_end": "2025-01-02T00:00:00+00:00",
        "partition": "2025-01-01",
    }
    assert (
        s.interval_manifest("2025-01-01T03:00:00+03:00", "2025-01-02T03:00:00+03:00")
        == expected
    )
    assert (
        s.interval_manifest("2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z") == expected
    )
    next_day = s.interval_manifest("2025-01-02T00:00:00Z", "2025-01-03T00:00:00Z")
    assert next_day["partition"] == "2025-01-02"


@pytest.mark.parametrize(
    "start,end",
    [
        ("2025-01-01", "2025-01-02"),
        ("2025-01-02T00:00:00Z", "2025-01-01T00:00:00Z"),
        ("2025-01-01T00:00:00Z", "2025-01-01T01:00:00Z"),
    ],
)
def test_invalid_intervals(start, end):
    with pytest.raises(ValueError):
        s.interval_manifest(start, end)


def test_failure_retry_and_no_double_publish():
    state = {
        "run_key": "key",
        "artifact_path": "/work/runs/key",
        "status": "evaluated",
        "interval": {"partition": "2025-01-01"},
    }
    before = copy.deepcopy(state)
    calls = []

    def failure(value):
        raise RuntimeError("before publish")

    with pytest.raises(RuntimeError):
        s.resume_publish(state, failure)
    assert state == before

    def publish(value):
        calls.append(value["run_key"])
        return {"version": "7"}

    result = s.resume_publish(state, publish)
    assert (
        state == before
        and result["status"] == "published"
        and result["release"] == {"version": "7"}
    )
    assert result["interval"] == state["interval"]
    assert s.resume_publish(result, publish) == result
    assert calls == ["key"]

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


@pytest.mark.parametrize(
    "start,end,partition",
    [
        ("2024-02-29T00:00:00Z", "2024-03-01T00:00:00Z", "2024-02-29"),
        ("2025-12-31T00:00:00Z", "2026-01-01T00:00:00Z", "2025-12-31"),
        ("2025-02-01T01:00:00+02:00", "2025-02-02T01:00:00+02:00", "2025-01-31"),
        ("2025-01-01T19:00:00-05:00", "2025-01-02T19:00:00-05:00", "2025-01-02"),
    ],
)
def test_interval_calendar_boundaries(start, end, partition):
    result = s.interval_manifest(start, end)
    assert result["partition"] == partition
    assert result["data_interval_start"].endswith("+00:00")
    assert result["data_interval_end"].endswith("+00:00")
    assert (
        s.interval_manifest(result["data_interval_start"], result["data_interval_end"])
        == result
    )


@pytest.mark.parametrize(
    "start,end",
    [
        ("2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z"),
        ("2025-01-01T00:00:00Z", "2025-01-02T00:00:01Z"),
        ("2025-01-01T00:00:00", "2025-01-02T00:00:00Z"),
        ("2025-01-01T00:00:00Z", "2025-01-02T00:00:00"),
        ("not-a-date", "2025-01-02T00:00:00Z"),
    ],
)
def test_invalid_or_unequal_daily_intervals(start, end):
    with pytest.raises(ValueError):
        s.interval_manifest(start, end)


def test_resume_passes_original_context_and_propagates_repeated_failure():
    state = {
        "run_key": "original-key",
        "artifact_path": "/work/original",
        "status": "evaluated",
        "interval": {
            "data_interval_start": "2025-12-31T00:00:00+00:00",
            "data_interval_end": "2026-01-01T00:00:00+00:00",
            "partition": "2025-12-31",
        },
    }
    before = copy.deepcopy(state)
    calls = []

    def fail(value):
        calls.append(copy.deepcopy(value))
        raise ConnectionError("publish unavailable")

    for _ in range(2):
        with pytest.raises(ConnectionError, match="publish unavailable"):
            s.resume_publish(state, fail)
        assert state == before
    assert calls == [before, before]


def test_already_published_context_never_calls_callback():
    state = {
        "run_key": "key",
        "artifact_path": "/work/key",
        "status": "published",
        "interval": {"partition": "2025-01-01"},
        "release": {"version": "7"},
    }
    before = copy.deepcopy(state)

    def forbidden(value):
        pytest.fail("already published state must not publish again")

    assert s.resume_publish(state, forbidden) == before
    assert state == before

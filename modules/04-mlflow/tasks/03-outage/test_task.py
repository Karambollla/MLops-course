"""Offline проверки поведения; исходная заготовка должна быть RED."""

import pytest
from course_tasks import load_solution, read_json

s = load_solution(__file__)


def pending():
    return {
        "run_key": "key-1",
        "run_id": "run-7",
        "artifact_uri": "runs:/run-7/model",
        "status": "pending",
        "champion_version": "4",
    }


def test_outage_and_recovery_preserve_origin(tmp_path):
    p = tmp_path / "pending.json"

    def unavailable(payload):
        raise ConnectionError("offline")

    result = s.recover_registration(pending(), unavailable, p)
    assert result == pending() and read_json(p) == pending()
    calls = []

    def available(payload):
        calls.append(payload.copy())
        return "8"

    restored = s.recover_registration(result, available, p)
    assert restored == dict(pending(), status="registered", version="8")
    assert read_json(p) == restored and len(calls) == 1
    assert (
        s.recover_registration(restored, available, p) == restored and len(calls) == 1
    )
    assert restored["champion_version"] == "4"


def test_unexpected_error_is_not_swallowed(tmp_path):
    def broken(payload):
        raise ValueError("invalid model")

    with pytest.raises(ValueError, match="invalid model"):
        s.recover_registration(pending(), broken, tmp_path / "state.json")

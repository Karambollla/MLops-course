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


def test_repeated_outage_keeps_input_and_durable_origin(tmp_path):
    original = pending()
    path = tmp_path / "nested" / "state" / "pending.json"
    calls = []

    def unavailable(payload):
        calls.append(payload.copy())
        raise ConnectionError("still offline")

    for _ in range(3):
        result = s.recover_registration(original, unavailable, path)
        assert result == pending()
        assert original == pending()
        assert read_json(path) == pending()
    assert calls == [pending()] * 3


def test_already_registered_never_calls_registration(tmp_path):
    registered = dict(pending(), status="registered", version="19")

    def forbidden(payload):
        pytest.fail("registered state must not register again")

    assert (
        s.recover_registration(registered, forbidden, tmp_path / "state.json")
        == registered
    )
    assert registered == dict(pending(), status="registered", version="19")


def test_success_preserves_origin_without_promoting_champion(tmp_path):
    original = pending()
    seen = []

    def register(payload):
        seen.append(payload.copy())
        return "23"

    result = s.recover_registration(original, register, tmp_path / "state.json")
    assert seen == [pending()]
    assert result == dict(pending(), status="registered", version="23")
    assert read_json(tmp_path / "state.json") == result

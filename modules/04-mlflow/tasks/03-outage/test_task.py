"""Offline проверки поведения; исходная заготовка должна быть RED."""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
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


@pytest.mark.integration
@pytest.mark.writes
def test_server_recovery_registers_original_source_once(tmp_path, mlflow_server):
    """Inject a pre-request outage; the uncertain post-commit window is separate."""
    server = mlflow_server
    frame = pd.DataFrame({"x": np.linspace(0, 1, 20)})
    pipeline = Pipeline([("model", Ridge(alpha=0.2))]).fit(frame, 2 * frame.x)
    with server.sdk.start_run(experiment_id=server.experiment_id) as run:
        logged = server.sdk.sklearn.log_model(
            pipeline,
            name="model",
            input_example=frame.iloc[:2],
            signature=server.sdk.models.infer_signature(frame, pipeline.predict(frame)),
        )
        run_id = run.info.run_id
    champion = server.sdk.register_model(logged.model_uri, server.model_name)
    server.client.set_registered_model_alias(
        server.model_name, "champion", champion.version
    )
    original = {
        "run_key": server.name,
        "run_id": run_id,
        "artifact_uri": logged.model_uri,
        "status": "pending",
        "champion_version": str(champion.version),
    }
    state_path = tmp_path / "pending.json"

    def unavailable(payload):
        raise ConnectionError("injected before SDK request; server stays running")

    waiting = s.recover_registration(original, unavailable, state_path)
    assert waiting == original == read_json(state_path)
    calls = []

    def register(payload):
        calls.append(payload.copy())
        assert payload["run_id"] == run_id
        return str(
            server.sdk.register_model(
                payload["artifact_uri"], server.model_name
            ).version
        )

    recovered = s.recover_registration(waiting, register, state_path)
    assert recovered == dict(
        original, status="registered", version=recovered["version"]
    )
    assert recovered == read_json(state_path)
    assert s.recover_registration(recovered, register, state_path) == recovered
    assert len(calls) == 1
    versions = server.client.search_model_versions(f"name='{server.model_name}'")
    assert len(versions) == 2  # original champion + one recovered registration
    restored = server.client.get_model_version(server.model_name, recovered["version"])
    assert restored.run_id == run_id and restored.source
    assert (
        server.client.get_model_version_by_alias(server.model_name, "champion").version
        == champion.version
    )

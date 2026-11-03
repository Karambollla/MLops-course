import os
from types import SimpleNamespace
from unittest.mock import Mock

import json

import pytest
from course_tasks import load_solution, load_task

s = load_solution(__file__)


def test_secret_is_not_returned():
    result = s.inspect_payload(
        {"data": {"data": {"artifact_key": "private-demo"}, "metadata": {"version": 1}}}
    )
    assert result == {"field_present": True}
    assert "private-demo" not in json.dumps(result)


@pytest.mark.parametrize(
    "payload", [{}, {"data": {"data": {}}}, {"data": {"data": None}}]
)
def test_missing_field(payload):
    with pytest.raises(ValueError):
        s.inspect_payload(payload)


@pytest.mark.parametrize("secret", ["another-demo-key", "секрет-для-теста", ""])
def test_only_field_presence_is_returned_without_printing_secrets(secret, capsys):
    result = s.inspect_payload(
        {
            "request_id": "demo-request",
            "data": {
                "data": {"artifact_key": secret, "another_secret": "not-for-output"},
                "metadata": {"version": 3},
            },
        }
    )
    assert result == {"field_present": True}
    captured = capsys.readouterr()
    printed = captured.out + captured.err
    assert "not-for-output" not in printed
    if secret:
        assert secret not in printed


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "invalid",
        {"data": None},
        {"data": []},
        {"data": {"data": []}},
        {"data": {"data": "invalid"}},
    ],
)
def test_malformed_nested_payload_has_a_value_error(payload):
    with pytest.raises(ValueError):
        s.inspect_payload(payload)


def test_read_secret_uses_kv2_and_redacts_payload(capsys):
    kv2 = SimpleNamespace(
        read_secret_version=Mock(
            return_value={"data": {"data": {"artifact_key": "private-sdk-value"}}}
        )
    )
    client = SimpleNamespace(secrets=SimpleNamespace(kv=SimpleNamespace(v2=kv2)))
    assert s.read_secret(client, path="housing", mount_point="secret") == {
        "field_present": True
    }
    kwargs = kv2.read_secret_version.call_args.kwargs
    assert kwargs["path"] == "housing"
    assert kwargs["mount_point"] == "secret"
    assert kv2.read_secret_version.call_count == 1
    captured = capsys.readouterr()
    assert "private-sdk-value" not in captured.out + captured.err


@pytest.mark.parametrize("error", [PermissionError("denied"), TimeoutError("timeout")])
def test_sdk_read_errors_reach_caller_without_retry(error):
    read = Mock(side_effect=error)
    client = SimpleNamespace(
        secrets=SimpleNamespace(
            kv=SimpleNamespace(v2=SimpleNamespace(read_secret_version=read))
        )
    )
    with pytest.raises(type(error)):
        s.read_secret(client)
    assert read.call_count == 1


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1", reason="Existing Vault opt-in"
)
def test_live_limited_token_reads_only_its_path(capsys):
    assert s.hvac is not None, "Install labs/vault/requirements.txt"
    client = s.hvac.Client(
        url=os.environ["VAULT_ADDR"], token=os.environ["VAULT_TOKEN"], timeout=5
    )
    assert s.read_secret(client, path="housing") == {"field_present": True}
    with pytest.raises(s.hvac.exceptions.Forbidden):
        s.read_secret(client, path=os.getenv("VAULT_DENIED_PATH", "neighbor"))
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""


@pytest.mark.sdk
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_SDK") != "1", reason="Installed hvac SDK opt-in"
)
def test_student_read_traverses_real_hvac_kv2_api(monkeypatch):
    assert s.hvac is not None, "Install labs/vault/requirements.txt"
    client = s.hvac.Client(
        url="http://vault.invalid:8200", token="temporary-offline-token", timeout=1
    )
    transport = Mock(
        return_value={"data": {"data": {"artifact_key": "private-offline-key"}}}
    )
    monkeypatch.setattr(client.adapter, "get", transport)
    assert s.read_secret(client, path="housing", mount_point="secret") == {
        "field_present": True
    }
    assert transport.call_count == 1
    args, kwargs = transport.call_args
    assert (args[0] if args else kwargs["url"]) == "/v1/secret/data/housing"


@pytest.mark.sdk
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_SDK") != "1", reason="Installed hvac exceptions opt-in"
)
@pytest.mark.parametrize(
    "kind,classification",
    [("forbidden", "access_denied"), ("timeout", "network_timeout")],
)
def test_real_hvac_errors_are_not_retried_or_replaced(
    monkeypatch, kind, classification
):
    assert s.hvac is not None, "Install labs/vault/requirements.txt"
    client = s.hvac.Client(
        url="http://vault.invalid:8200", token="temporary-offline-token", timeout=1
    )
    error = s.hvac.exceptions.Forbidden() if kind == "forbidden" else s.Timeout()
    transport = Mock(side_effect=error)
    monkeypatch.setattr(client.adapter, "get", transport)
    with pytest.raises(type(error)):
        s.read_secret(client)
    assert transport.call_count == 1
    expiry = load_task("10-vault/02-expiry")
    assert (
        expiry.classify_error(
            status=403 if kind == "forbidden" else None, timeout=kind == "timeout"
        )
        == classification
    )

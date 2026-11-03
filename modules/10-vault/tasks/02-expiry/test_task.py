import os
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from course_tasks import load_solution, load_task

s = load_solution(__file__)


@pytest.mark.parametrize(
    "status,timeout,expected",
    [
        (403, False, "access_denied"),
        (None, True, "network_timeout"),
        (200, False, "ok"),
        (204, False, "ok"),
        (500, False, "http_error"),
        (404, False, "http_error"),
    ],
)
def test_error_classification(status, timeout, expected):
    assert s.classify_error(status, timeout) == expected


@pytest.mark.parametrize(
    "status,expected",
    [
        (199, "http_error"),
        (200, "ok"),
        (201, "ok"),
        (299, "ok"),
        (300, "http_error"),
        (401, "http_error"),
        (503, "http_error"),
    ],
)
def test_success_is_the_entire_2xx_range(status, expected):
    assert s.classify_error(status, timeout=False) == expected


@pytest.mark.parametrize("status", [None, 200, 403, 500])
def test_timeout_has_priority_over_http_status(status):
    assert s.classify_error(status, timeout=True) == "network_timeout"


def test_renew_self_returns_only_lifetime_metadata(capsys):
    token = SimpleNamespace(
        renew_self=Mock(
            return_value={
                "auth": {
                    "client_token": "private-child-token",
                    "lease_duration": 60,
                    "renewable": True,
                }
            }
        )
    )
    client = SimpleNamespace(auth=SimpleNamespace(token=token))
    assert s.renew_token(client, increment="45s") == {
        "ttl_seconds": 60,
        "renewable": True,
    }
    token.renew_self.assert_called_once_with(increment="45s")
    captured = capsys.readouterr()
    assert "private-child-token" not in captured.out + captured.err


def test_revoke_uses_self_endpoint():
    token = SimpleNamespace(revoke_self=Mock(return_value=None))
    assert s.revoke_token(SimpleNamespace(auth=SimpleNamespace(token=token))) == {
        "revoked": True
    }
    token.revoke_self.assert_called_once_with()


@pytest.mark.integration
@pytest.mark.writes
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1" or os.getenv("MLOPS_RUN_WRITES") != "1",
    reason="Temporary token writes require both integration and writes opt-in",
)
def test_live_renew_and_revoke_only_a_new_child_token():
    assert s.hvac is not None, "Install labs/vault/requirements.txt"
    admin = s.hvac.Client(
        url=os.environ["VAULT_ADDR"], token=os.environ["VAULT_ADMIN_TOKEN"], timeout=5
    )
    created = admin.auth.token.create(
        policies=[os.getenv("VAULT_TEST_POLICY", "housing")],
        ttl="60s",
        renewable=True,
        display_name="mlops-temporary-sdk-test",
    )
    child_token = created["auth"]["client_token"]
    child = s.hvac.Client(url=os.environ["VAULT_ADDR"], token=child_token, timeout=5)
    policy = load_task("10-vault/01-policy")
    try:
        assert policy.read_secret(child) == {"field_present": True}
        renewed = s.renew_token(child, increment="60s")
        assert set(renewed) == {"ttl_seconds", "renewable"}
        assert renewed["ttl_seconds"] > 0 and renewed["renewable"] is True
        assert s.revoke_token(child) == {"revoked": True}
        with pytest.raises(s.hvac.exceptions.Forbidden):
            policy.read_secret(child)
    finally:
        # Cleanup targets only the token this test just created, even if a student stub fails.
        admin.auth.token.revoke(child_token)

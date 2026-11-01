import json

import pytest
from course_tasks import load_solution

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

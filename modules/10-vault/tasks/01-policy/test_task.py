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

import pytest
from course_tasks import load_solution

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

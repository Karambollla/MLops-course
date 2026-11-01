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

import pytest
from course_tasks import load_solution

s = load_solution(__file__)
FIRST = "PLAY RECAP ***\nnode : ok=2 changed=2 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0\n"
SECOND = FIRST.replace("changed=2", "changed=0")


def test_recap_parses_counts_and_second_run_is_idempotent():
    assert s.parse_recap(FIRST)["node"]["changed"] == 2
    assert s.compare_runs(FIRST, SECOND) == {"node": 0}


@pytest.mark.parametrize(
    "text",
    [
        "",
        "TASK changed: [node]",
        SECOND.replace("failed=0", "failed=1"),
        SECOND.replace("changed=0", "changed=1"),
    ],
)
def test_bad_or_non_idempotent_repeat_is_not_accepted(text):
    with pytest.raises(ValueError):
        s.compare_runs(FIRST, text)

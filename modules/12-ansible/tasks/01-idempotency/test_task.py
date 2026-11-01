import json
import subprocess
import sys
from pathlib import Path

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


@pytest.mark.parametrize(
    "first,second",
    [
        (FIRST.replace("failed=0", "failed=1"), SECOND),
        (FIRST, SECOND.replace("node :", "other :")),
        (FIRST, SECOND.replace("unreachable=0", "unreachable=1")),
    ],
)
def test_errors_and_different_hosts_are_rejected(first, second):
    with pytest.raises(ValueError):
        s.compare_runs(first, second)


MULTI_FIRST = """PLAY [Local fixture] ***
TASK [Configure] ***
changed: [node-a]
PLAY RECAP *********************************************************************
node-a : ok=8 changed=2 unreachable=0 failed=0 skipped=3 rescued=1 ignored=2
node_b : ok=5 changed=1 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
"""
MULTI_SECOND = """PLAY RECAP ***
node_b : ok=5 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
node-a : ok=8 changed=0 unreachable=0 failed=0 skipped=3 rescued=1 ignored=2
"""


def test_all_recap_counters_and_multiple_hosts():
    assert s.parse_recap(MULTI_FIRST) == {
        "node-a": {
            "ok": 8,
            "changed": 2,
            "unreachable": 0,
            "failed": 0,
            "skipped": 3,
            "rescued": 1,
            "ignored": 2,
        },
        "node_b": {
            "ok": 5,
            "changed": 1,
            "unreachable": 0,
            "failed": 0,
            "skipped": 0,
            "rescued": 0,
            "ignored": 0,
        },
    }
    assert s.compare_runs(MULTI_FIRST, MULTI_SECOND) == {"node-a": 0, "node_b": 0}


@pytest.mark.parametrize("text", ["", "TASK [No recap] ***\nok: [node]"])
def test_parser_requires_a_recap(text):
    with pytest.raises(ValueError):
        s.parse_recap(text)


@pytest.mark.parametrize("run", ["first", "second"])
@pytest.mark.parametrize("field", ["failed", "unreachable"])
def test_failure_of_any_host_in_either_run_is_rejected(run, field):
    first, second = MULTI_FIRST, MULTI_SECOND
    if run == "first":
        first = first.replace(f"{field}=0", f"{field}=1", 1)
    else:
        second = second.replace(f"{field}=0", f"{field}=1", 1)
    with pytest.raises(ValueError):
        s.compare_runs(first, second)


def test_missing_host_in_second_run_is_rejected():
    with pytest.raises(ValueError):
        s.compare_runs(MULTI_FIRST, SECOND.replace("node :", "node-a :"))


def test_cli_reads_two_recap_paths_with_spaces(tmp_path):
    first, second = tmp_path / "first recap.txt", tmp_path / "second recap.txt"
    first.write_text(MULTI_FIRST)
    second.write_text(MULTI_SECOND)
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("solution.py")),
            str(first),
            str(second),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"node-a": 0, "node_b": 0}

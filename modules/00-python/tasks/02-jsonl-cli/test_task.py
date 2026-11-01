"""Offline проверки поведения; исходная заготовка должна быть RED."""

import re
import subprocess
import sys
from pathlib import Path

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_iterator_is_lazy_and_counts_lines():
    def source():
        yield '{"duration": 2}\n'
        yield "broken\n"
        raise AssertionError("Нельзя читать после повреждённой строки")

    records = iter(s.iter_records(source()))
    assert next(records) == {"duration": 2}
    with pytest.raises(ValueError, match="2"):
        next(records)


def test_summary_and_invalid_duration():
    result = s.summarize_file(Path(__file__).parent / "fixtures" / "valid.jsonl")
    assert result == {"count": 2, "mean": 3.0}


@pytest.mark.parametrize("line", ["[]", "", "null"])
def test_json_object_required(line):
    with pytest.raises(ValueError, match="1"):
        list(s.iter_records([line]))


def test_cli_reports_bad_line():
    task = Path(__file__).parent
    result = subprocess.run(
        [
            sys.executable,
            str(task / "solution.py"),
            str(task / "fixtures" / "broken.jsonl"),
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert re.search(r"(?i)(line|строк\w*)\s*[:#]?\s*2\b", result.stderr)
    assert "Traceback" not in result.stderr
    assert not result.stdout.strip()

"""Offline проверки поведения; исходная заготовка должна быть RED."""

import re
import subprocess
import sys
from pathlib import Path

import pytest
import json
from course_tasks import load_task
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


@pytest.mark.parametrize(
    "content, expected",
    [
        ("", {"count": 0, "mean": None}),
        (
            '{"duration":0.25,"note":"привет"}\n{"duration":1.5}\n',
            {"count": 2, "mean": 0.875},
        ),
    ],
)
def test_cli_success_is_one_json_value(tmp_path, content, expected):
    path = tmp_path / "данные с пробелами.jsonl"
    path.write_text(content, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("solution.py")), str(path)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == expected
    assert s.summarize_file(path) == expected


@pytest.mark.parametrize("bad", ['"text"', "42", "true", "[{}]", "null", " ", "{"])
@pytest.mark.parametrize("prefix", [[], ['{"duration":2}\n', "{}\n"]])
def test_bad_json_line_is_reported_lazily(bad, prefix):
    seen = []

    def source():
        for line in prefix + [bad]:
            seen.append(line)
            yield line
        raise AssertionError("Чтение после ошибки")

    records = iter(s.iter_records(source()))
    assert seen == []
    for line in prefix:
        assert next(records) == json.loads(line)
    with pytest.raises(ValueError, match=rf"\b{len(prefix) + 1}\b"):
        next(records)
    assert len(seen) == len(prefix) + 1


def test_summary_reuses_aggregator_with_stream(tmp_path, monkeypatch):
    previous = load_task("00-python/01-records")
    original_aggregate = previous.summarize
    calls = []

    def aggregate(records):
        assert not isinstance(records, (list, tuple))
        iterator = iter(records)
        calls.append(next(iterator))
        with pytest.raises(ValueError):
            next(iterator)
        return {"count": 123, "mean": 4.5}

    monkeypatch.setattr(previous, "summarize", aggregate)
    # Also support importing the shared function once at module import time.
    for name, value in list(vars(s).items()):
        if value is original_aggregate:
            monkeypatch.setattr(s, name, aggregate)
    path = tmp_path / "stream.jsonl"
    path.write_text('{"duration":2}\nbroken\n', encoding="utf-8")
    assert s.summarize_file(path) == {"count": 123, "mean": 4.5}
    assert calls == [{"duration": 2}]


@pytest.mark.parametrize("prefix", [[], ['{"duration":2}\n', "{}\n"]])
def test_cli_reports_first_or_later_malformed_line(tmp_path, prefix):
    path = tmp_path / "bad.jsonl"
    path.write_text("".join(prefix) + "broken\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("solution.py")), str(path)],
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    line_number = len(prefix) + 1
    assert re.search(rf"(?i)(line|строк\w*)\s*[:#]?\s*{line_number}\b", result.stderr)
    assert not result.stdout.strip()

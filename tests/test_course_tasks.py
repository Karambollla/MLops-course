"""Tests for task navigation/loading, not student exercise implementations."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from course_tasks import load_solution, load_task, task_directory

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def course(tmp_path, monkeypatch):
    module = tmp_path / "modules" / "00-demo" / "tasks"
    for slug, value in [("01-first", 7), ("02-second", 11)]:
        task = module / slug
        task.mkdir(parents=True)
        (task / "solution.py").write_text(f"VALUE = {value}\n", encoding="utf-8")
        (task / "test_task.py").write_text("", encoding="utf-8")
    catalog = {
        "schema_version": 1,
        "tasks": [
            {
                "id": "00-demo/01-first",
                "title": "Первое",
                "starter": "solution.py",
                "tests": "test_task.py",
            },
            {
                "id": "00-demo/02-second",
                "title": "Второе",
                "starter": "solution.py",
                "tests": "test_task.py",
            },
        ],
    }
    (tmp_path / "modules" / "tasks.json").write_text(
        json.dumps(catalog), encoding="utf-8"
    )
    monkeypatch.setenv("MLOPS_COURSE_ROOT", str(tmp_path))
    return tmp_path


def test_loader_keeps_identically_named_starters_independent(course):
    first = load_task("00-demo/01-first")
    second = load_task("00-demo/02-second")
    assert first.VALUE == 7
    assert second.VALUE == 11
    assert first.__name__ != second.__name__


def test_load_solution_resolves_the_current_task(course):
    test = course / "modules/00-demo/tasks/01-first/test_task.py"
    assert load_solution(test) is load_task("00-demo/01-first")


@pytest.mark.parametrize(
    "task_id",
    ["../outside", "00-demo/../../outside", "/tmp/outside", "00-demo/99-unknown", ""],
)
def test_unregistered_or_escaping_task_is_rejected(course, task_id):
    with pytest.raises(ValueError):
        task_directory(task_id)


def test_loader_does_not_follow_a_starter_outside_the_task(course, tmp_path):
    outside = course / "outside.py"
    outside.write_text("VALUE = 'outside'\n")
    task = course / "modules/00-demo/tasks/01-first"
    (task / "escape.py").symlink_to(outside)
    with pytest.raises(ValueError):
        load_task("00-demo/01-first", filename="escape.py")
    with pytest.raises(ValueError):
        load_task("00-demo/01-first", filename="../../outside.py")


def test_missing_student_file_has_a_clear_error(course):
    with pytest.raises(FileNotFoundError, match="missing.py"):
        load_task("00-demo/01-first", filename="missing.py")


def invoke(course, *args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_task.py"), *args],
        cwd=course,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )


def test_runner_lists_registered_tasks(course):
    result = invoke(course, "list")
    assert result.returncode == 0, result.stderr
    assert "00-demo/01-first" in result.stdout
    assert "00-demo/02-second" in result.stdout


def test_runner_only_executes_the_selected_task_tests(course):
    first = course / "modules/00-demo/tasks/01-first/test_task.py"
    second = course / "modules/00-demo/tasks/02-second/test_task.py"
    first.write_text("def test_selected():\n    assert True\n")
    second.write_text(
        "def test_unselected():\n    raise AssertionError('unselected task was executed')\n"
    )
    result = invoke(course, "test", "00-demo/01-first", "--", "-q")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 passed" in result.stdout
    assert "unselected task was executed" not in result.stdout


def test_runner_forwards_cli_arguments_without_shell_interpretation(course):
    solution = course / "modules/00-demo/tasks/01-first/solution.py"
    solution.write_text(
        "import sys\nif __name__ == '__main__':\n    print('|'.join(sys.argv[1:]))\n"
    )
    result = invoke(
        course, "run", "00-demo/01-first", "--", "--input", "a file.jsonl", "$(example)"
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "--input|a file.jsonl|$(example)"


def test_runner_rejects_a_missing_id_instead_of_running_everything(course):
    result = invoke(course, "test")
    assert result.returncode == 2
    assert "TASK" in result.stderr or "задани" in result.stderr

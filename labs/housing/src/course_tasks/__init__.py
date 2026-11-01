"""Locate and load the course's task-local student files without name collisions."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

_ID_PART = re.compile(r"[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def course_root() -> Path:
    explicit = os.environ.get("MLOPS_COURSE_ROOT")
    candidates = (
        [Path(explicit).expanduser().resolve()]
        if explicit
        else Path(__file__).resolve().parents
    )
    for candidate in candidates:
        if (candidate / "modules" / "tasks.json").is_file():
            return candidate
    raise FileNotFoundError(
        "Не найден modules/tasks.json. Установи пакет по SETUP.md или задай MLOPS_COURSE_ROOT."
    )


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def task_catalog() -> list[dict[str, Any]]:
    catalog = read_json(course_root() / "modules" / "tasks.json")
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("tasks"), list):
        raise ValueError("Неподдерживаемая структура modules/tasks.json")
    tasks = catalog["tasks"]
    identifiers = [task["id"] for task in tasks]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Повторяющиеся идентификаторы заданий в modules/tasks.json")
    return tasks


def task_directory(task_id: str) -> Path:
    parts = task_id.split("/")
    if len(parts) != 2 or not all(_ID_PART.fullmatch(part) for part in parts):
        raise ValueError("Идентификатор задания должен иметь вид 00-python/01-records")
    if task_id not in {task["id"] for task in task_catalog()}:
        raise ValueError(f"Неизвестное задание: {task_id}. Посмотри make task-list.")
    root = course_root()
    directory = (root / "modules" / parts[0] / "tasks" / parts[1]).resolve()
    if not directory.is_relative_to(root / "modules"):
        raise ValueError("Папка задания выходит за пределы modules")
    if not directory.is_dir():
        raise FileNotFoundError(f"Нет папки задания: {directory}")
    return directory


def _load_file(directory: Path, filename: str) -> ModuleType:
    path = (directory / filename).resolve()
    if not path.is_relative_to(directory):
        raise ValueError("Файл заготовки должен находиться внутри папки задания")
    if not path.is_file():
        raise FileNotFoundError(f"Нет файла заготовки: {path}")
    name = "course_student_" + hashlib.sha256(str(path).encode()).hexdigest()[:20]
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Не удалось загрузить Python-заготовку: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def load_task(task_id: str, filename: str = "solution.py") -> ModuleType:
    return _load_file(task_directory(task_id), filename)


def load_solution(test_file: str | Path, filename: str = "solution.py") -> ModuleType:
    path = Path(test_file).resolve()
    root = course_root()
    for directory in [path.parent, *path.parents]:
        if directory.parent.name != "tasks":
            continue
        task_id = f"{directory.parent.parent.name}/{directory.name}"
        expected = task_directory(task_id)
        if directory != expected or not path.is_relative_to(root):
            raise ValueError("Тест не принадлежит зарегистрированной папке задания")
        return _load_file(expected, filename)
    raise ValueError("Тест должен находиться в modules/<module>/tasks/<task>/")

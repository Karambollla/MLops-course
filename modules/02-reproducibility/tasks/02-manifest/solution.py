"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

from copy import deepcopy
from pathlib import Path

from course_tasks import load_task
from housing.features import FEATURES


def build_manifest(
    data_path: Path, seed: int, split: dict, versions: dict, parameters: dict
) -> dict:
    # TODO: хеш и метаданные, независимая копия split/parameters.
    raise NotImplementedError("Собери манифест")


def validate_bundle(bundle: dict, manifest: dict, expected_sha256: str) -> None:
    # TODO: совместимость до predict, явный ValueError.
    raise NotImplementedError("Проверь контракт bundle")

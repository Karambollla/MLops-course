"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import json
from pathlib import Path

import joblib
import numpy as np

from course_tasks import load_task
from housing.features import FEATURES


def compare_runs(first: Path, second: Path, batch) -> dict:
    # TODO: provenance, контракт, predictions и метрики с допуском.
    raise NotImplementedError("Сравни восстановленные запуски")

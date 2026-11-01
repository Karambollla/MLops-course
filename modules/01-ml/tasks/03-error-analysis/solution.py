"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import numpy as np
import pandas as pd

from course_tasks import load_task
from housing.features import FEATURES, TARGET


def quartile_errors(y_true, y_pred) -> list[dict]:
    # TODO: qcut, размеры и метрики из baseline.
    raise NotImplementedError("Проанализируй ошибки")


def geographic_split(frame, latitude_cutoff: float) -> dict:
    # TODO: разделение по географии с исходными индексами.
    raise NotImplementedError("Раздели регионы")

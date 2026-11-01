"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

from copy import deepcopy
from datetime import datetime, timedelta, timezone


def interval_manifest(start: str, end: str) -> dict:
    # TODO: aware datetime, UTC, границы одного дня без now().
    raise NotImplementedError("Зафиксируй интервал")


def resume_publish(state: dict, publish_fn) -> dict:
    # TODO: retry опубликованного шага без дубля и без мутации state.
    raise NotImplementedError("Восстанови шаг publish")

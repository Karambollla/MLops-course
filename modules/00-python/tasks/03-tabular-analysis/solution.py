"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

from pathlib import Path

import pandas as pd


def describe_frame(frame) -> dict:
    # TODO: shape, dtype, пропуски, квантили.
    raise NotImplementedError("Опиши таблицу")


def align_series(left, right) -> tuple:
    # TODO: явное выравнивание по меткам.
    raise NotImplementedError("Выровняй индексы")


def write_report(csv_path: Path, output: Path) -> None:
    # TODO: read_csv и Markdown, создание parent directory.
    raise NotImplementedError("Сохрани сводку")

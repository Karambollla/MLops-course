"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import json
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

from course_tasks import load_task


def iter_records(stream: Iterable[str]) -> Iterator[dict]:
    # TODO: ленивое чтение с диагностикой номера строки.
    raise NotImplementedError("Реализуй iter_records")


def summarize_file(path: Path) -> dict:
    # TODO: load_task('00-python/01-records'), потоковый подсчёт.
    raise NotImplementedError("Реализуй summarize_file")


def main() -> None:
    # TODO: argparse, stdout JSON, stderr и exit != 0 при ошибке.
    raise NotImplementedError("Реализуй CLI JSONL")


if __name__ == "__main__":
    main()

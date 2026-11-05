"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import math


def summarize(records: list[dict]) -> dict:
    count = 0
    total = 0.0

    for record in records:
        val = record.get("duration")
        if isinstance(val, (int, float)) and not isinstance(val, bool) and 0 < val < float("inf"):
            count += 1
            total += val

    if count == 0:
        return {"count": 0, "mean": None}

    return {"count": count, "mean": total / count}


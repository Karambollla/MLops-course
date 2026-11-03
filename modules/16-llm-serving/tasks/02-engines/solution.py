"""Измерение клиентского streaming; timestamps берутся monotonic clock."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import json
import math
from time import monotonic


from course_tasks import load_task


def request_metrics(
    started: float, events: list[dict], ended: float, output_tokens: int
) -> dict:
    raise NotImplementedError(
        "Найди первый непустой content и вычисли объявленные метрики"
    )

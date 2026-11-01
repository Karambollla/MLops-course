"""Показатели клиента: throughput считается по стенному времени, не сумме latency."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import json
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from urllib.request import Request, urlopen

import numpy as np

from course_tasks import load_task


def latency_summary(
    rows: list[dict], elapsed_seconds: float, min_requests: int = 200
) -> dict:
    raise NotImplementedError("Проверь измерения и вычисли latency/throughput/errors")

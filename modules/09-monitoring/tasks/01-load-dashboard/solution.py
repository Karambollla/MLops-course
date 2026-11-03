"""Реализуй функцию по контракту README и прямым тестам."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import json
import math
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from urllib.request import Request, urlopen

import numpy as np


def summarize_run(run):
    """Вычисли RPS/error ratio; не называй нулевой трафик успешным обслуживанием."""
    # TODO(student): реализуй контракт из README и тестов.
    raise NotImplementedError("summarize_run")


def measure_load(
    url: str, payload: dict, requests: int = 200, concurrency: int = 1
) -> dict:
    """Измерить настоящие predict-запросы и вернуть вход summarize_run."""
    # TODO: запросы через HTTP-клиент, latency каждого ответа, общий perf_counter.
    # HTTP 4xx/5xx записать в status_counts; сеть не выдавать за успешный ответ.
    # Вернуть concurrency/requests/seconds/status_counts/p95_seconds/durations_seconds.
    raise NotImplementedError("Измерь HTTP-нагрузку работающего housing API")

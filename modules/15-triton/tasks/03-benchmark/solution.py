"""Показатели клиента: throughput считается по стенному времени, не сумме latency."""

import numpy as np


def latency_summary(
    rows: list[dict], elapsed_seconds: float, min_requests: int = 200
) -> dict:
    raise NotImplementedError("Проверь измерения и вычисли latency/throughput/errors")

"""Добавь задачи SDK к текущему DAG, а не собственный цикл retry."""

from __future__ import annotations

# ruff: noqa: F401
from datetime import timedelta
from typing import Any

from housing.airflow_runtime import publish_release, quality_gate

try:
    from airflow.exceptions import AirflowFailException
    from airflow.sdk import get_current_context, task
except ModuleNotFoundError as error:
    if error.name != "airflow":
        raise
    AirflowFailException = get_current_context = task = None


def attach_release(metadata: Any) -> Any:
    if task is None:
        raise RuntimeError(
            "Airflow SDK отсутствует. Запусти проверки в контейнере labs/airflow по README модуля."
        )
    # TODO: создай @task gate и publish в активном DAG context.
    # gate: quality_gate(metadata, ctx['params']['gate_ratio']), отказ -> AirflowFailException.
    # publish: retries=1, retry_delay=timedelta(seconds=1), вызови publish_release.
    # После записи вызови RuntimeError, если fail_publish_once и ti.try_number == 1.
    # Верни TaskFlow-результат publish, связанного с gate(metadata).
    raise NotImplementedError("Подключи gate и publish через airflow.sdk")

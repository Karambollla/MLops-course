"""Получай интервал из контекста настоящей задачи, не из текущего времени."""

from __future__ import annotations

# ruff: noqa: F401
from typing import Any

from housing.airflow_runtime import interval_metadata

try:
    from airflow.sdk import get_current_context, task
    from airflow.timetables.interval import CronDataIntervalTimetable
except ModuleNotFoundError as error:
    if error.name != "airflow":
        raise
    get_current_context = task = CronDataIntervalTimetable = None


def daily_schedule() -> CronDataIntervalTimetable:
    if CronDataIntervalTimetable is None:
        raise RuntimeError(
            "Airflow SDK отсутствует. Запусти проверки в контейнере labs/airflow по README модуля."
        )
    # TODO: настоящий CronDataIntervalTimetable('0 0 * * *', timezone='UTC').
    raise NotImplementedError("Создай суточное расписание Airflow")


def attach_interval_context() -> Any:
    if task is None:
        raise RuntimeError(
            "Airflow SDK отсутствует. Запусти проверки в контейнере labs/airflow по README модуля."
        )
    # TODO: @task(task_id='prepare_interval'), get_current_context() внутри тела.
    # Передай ctx['data_interval_start/end'] готовой interval_metadata и верни XCom.
    raise NotImplementedError("Добавь задачу prepare_interval через airflow.sdk")

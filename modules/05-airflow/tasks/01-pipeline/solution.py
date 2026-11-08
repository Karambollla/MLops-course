"""Построй настоящий TaskFlow DAG. Условия и команды находятся в README.md."""

from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime, timezone

from course_tasks import load_task
from housing.airflow_runtime import prepare_training, run_training

try:
    from airflow.sdk import DAG, Param, dag, get_current_context, task
except ModuleNotFoundError as error:
    if error.name != "airflow":
        raise
    DAG = Param = dag = get_current_context = task = None


def build_dag(stage: int = 1) -> DAG:
    if dag is None:
        raise RuntimeError(
            "Airflow SDK отсутствует. Запусти проверки в контейнере labs/airflow по README модуля."
        )
    if isinstance(stage, bool) or stage not in (1, 2, 3):
        raise ValueError("stage должен быть 1, 2 или 3")
    # TODO: @dag с dag_id='housing_pipeline', Param и задачами @task.
    # 1: validate_data -> train_evaluate, чтение ctx['params'] только внутри task.
    # 2: внутри DAG подключи attach_release(metadata) следующего задания.
    # 3: подключи daily_schedule() и prepare_interval до validate_data.
    # Не вызывай prepare_training/run_training при построении графа.
    raise NotImplementedError("Построй DAG через airflow.sdk и верни объект DAG")

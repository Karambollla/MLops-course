"""Совместимый вход: канонический DAG размещён в задании05/01."""
from course_tasks import load_task

_task_module = load_task("05-airflow/01-pipeline", filename="housing_pipeline.py")

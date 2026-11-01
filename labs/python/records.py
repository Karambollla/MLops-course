"""Совместимый вход: учебная функция находится в modules/00-python/tasks/01-records/solution.py."""

from course_tasks import load_task


def summarize(records: list[dict]) -> dict:
    return load_task("00-python/01-records").summarize(records)

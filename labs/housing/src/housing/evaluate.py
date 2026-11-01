"""Совместимый API: метрики реализуются в modules/01-ml/tasks/01-baseline/solution.py."""

import numpy as np
from course_tasks import load_task


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return load_task("01-ml/01-baseline").regression_metrics(y_true, y_pred)

"""API метрик: определения берутся из сохранённого modules/01-ml/housing.ipynb."""

import numpy as np
from course_tasks.notebook import housing_notebook_path, load_notebook


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return load_notebook(housing_notebook_path()).regression_metrics(y_true, y_pred)

"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge

from course_tasks import load_task
from housing.features import FEATURES, TARGET
from housing.train import train

try:
    import mlflow
except ModuleNotFoundError as exc:
    if exc.name != "mlflow":
        raise
    mlflow = None


def select_candidate(runs: list[dict]) -> str:
    # TODO: проверка сопоставимости и выбор только по validation.
    raise NotImplementedError("Выбери run")


def track_experiments(
    data: Path,
    output: Path,
    tracking_uri: str,
    *,
    experiment_name: str = "housing-course",
) -> list[dict]:
    """Train three configurations and record their actual results with the SDK."""
    if mlflow is None:
        raise RuntimeError(
            "Install MLflow SDK: python -m pip install -r labs/mlflow/requirements.txt"
        )
    # TODO: set_tracking_uri / set_experiment(experiment_name) выбирают сервер и группу.
    # Для alpha=0.1/1.0/10.0 вызови train(..., seed=42, parameters={"alpha": alpha}).
    # Сначала реализуй этот режим train в сохранённом ML-notebook.
    # Для каждого run: реальные параметры/версии, четыре именованные метрики,
    # четыре файла обучения. Полный split хранится в artifact, не в params.
    # Методы SDK разобраны в ../../README.md, «Самостоятельный пример учёта».
    raise NotImplementedError("Залогируй три эксперимента")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("work/housing.csv"))
    parser.add_argument("--output", type=Path, default=Path("work/mlflow-runs"))
    parser.add_argument(
        "--tracking-uri",
        default=os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"),
    )
    args = parser.parse_args()
    track_experiments(args.data, args.output, args.tracking_uri)


if __name__ == "__main__":
    main()

"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path

import numpy as np
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
    if len(runs) != 3:
        raise ValueError
    cur_min = float("inf")
    cur_test = "O"
    for i in range(len(runs)):
        for metric in ("validation_mae", "validation_rmse"):
            value = runs[i][metric]
            if not np.isfinite(value) or value < 0:
                raise ValueError
        if runs[i]["status"] != "FINISHED":
            raise ValueError
        
        if runs[i]["validation_mae"] < cur_min:
            cur_test = runs[i]["run_id"]
            cur_min = runs[i]["validation_mae"]
        elif runs[i]["validation_mae"] == cur_min:
            cur_test = min(runs[i]["run_id"], cur_test)
        for j in range(i + 1, len(runs)):
            if (runs[i]["parameters"] == runs[j]["parameters"]) or (runs[i]["data_sha256"] != runs[j]["data_sha256"]) or (runs[i]["split"] != runs[j]["split"]):
                raise ValueError
    return cur_test


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
    # Для каждой конфигурации: start_run, своё обучение, log_params,
    # log_metrics и log_artifacts; значения берутся из настоящих результатов.
    # Пример этих SDK-вызовов: ../../README.md, «Самостоятельный пример учёта».
    configs = [
    {"model": "ridge", "alpha": 0.1},
    {"model": "ridge", "alpha": 1.0},
    {"model": "forest", "max_depth": 10},
    ]
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    runs = []
    for i, config in enumerate(configs):
        run_output = output / f"run_{i}"

        with mlflow.start_run() as run:
            train(data, run_output, seed=42, config=config)
            metrics = json.loads((run_output / "metrics.json").read_text())
            manifest = json.loads((run_output / "manifest.json").read_text())
            run_id = run.info.run_id


            split = json.loads((run_output / "split.json").read_text())
            data_sha256 = manifest["data_sha256"]
            candidate = metrics["candidate"]

            mlflow.log_params({"data_sha256": data_sha256})
            mlflow.log_params({"split": json.dumps(split)})
            mlflow.log_params(config)
            mlflow.log_params({"versions": json.dumps(manifest["versions"])})
            mlflow.log_metrics({
                "validation_mae": candidate["validation"]["mae"],
                "validation_rmse": candidate["validation"]["rmse"],
                "test_mae": candidate["test"]["mae"],
                "test_rmse": candidate["test"]["rmse"],
            })
            mlflow.log_artifacts(str(run_output))
        runs.append({
            "run_id": run_id,
            "status": "FINISHED",
            "parameters": manifest["parameters"],
            "data_sha256": data_sha256,
            "split": split,
            "validation_mae": candidate["validation"]["mae"],
            "validation_rmse": candidate["validation"]["rmse"],
        })
    (output / "comparison.json").write_text(
        json.dumps(runs, indent=2),
        encoding="utf-8",
    )
    return runs

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

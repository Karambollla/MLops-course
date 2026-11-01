"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import json
from pathlib import Path

import numpy as np

try:
    import mlflow
    import mlflow.sklearn
    from mlflow.models import infer_signature
    from mlflow.tracking import MlflowClient
except ModuleNotFoundError as exc:
    if exc.name != "mlflow":
        raise
    mlflow = infer_signature = MlflowClient = None


def resolve_release(client, model_name: str, alias: str, expected_run_id: str) -> dict:
    # TODO: закрепить конкретный номер версии и проверить источник.
    raise NotImplementedError("Разреши alias")


def register_model(
    pipeline, example, run_id: str, model_name: str, tracking_uri: str
) -> dict:
    """Register the trained Pipeline through the MLflow sklearn flavor."""
    if mlflow is None:
        raise RuntimeError(
            "Install MLflow SDK: python -m pip install -r labs/mlflow/requirements.txt"
        )
    # TODO: set_tracking_uri, схема через mlflow.models.infer_signature,
    # mlflow.sklearn.log_model и MlflowClient для версий и aliases.
    # Свяжи модель с переданным run_id и проверь прогнозы после загрузки.
    raise NotImplementedError("Зарегистрируй Pipeline")


def assert_parity(original, registered, batch) -> None:
    # TODO: одинаковый batch, конечность и allclose.
    raise NotImplementedError("Сравни registry и bundle")

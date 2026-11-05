"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import numpy as np

from housing.features import FEATURES


def check_prediction_response(payload: dict, expected, model_version: str) -> None:
    if set(payload) != {"predictions", "model_version", "target_unit"}:
        raise ValueError("Неверные ключи ответа")

    if payload["model_version"] != model_version:
        raise ValueError("Неверная версия модели")

    if payload["target_unit"] != "100000 USD":
        raise ValueError("Неверная единица измерения")

    predictions = np.asarray(payload["predictions"])
    expected = np.asarray(expected)

    if predictions.ndim != 1 or expected.ndim != 1:
        raise ValueError("Прогнозы должны быть одномерными")

    if predictions.shape != expected.shape:
        raise ValueError("Количество прогнозов не совпадает")

    if not np.isfinite(predictions).all():
        raise ValueError("Прогнозы должны быть конечными")

    if not np.allclose(predictions, expected, rtol=1e-6, atol=1e-8):
        raise ValueError("Прогнозы не совпадают")

def exercise_api(client, pipeline, batch, model_version: str) -> None:
    payload = {"instances": batch.to_dict(orient="records")}
    response = client.post("/predict", json=payload)
    expected = pipeline.predict(batch)
    check_prediction_response(response.json(), expected=expected, model_version=model_version)


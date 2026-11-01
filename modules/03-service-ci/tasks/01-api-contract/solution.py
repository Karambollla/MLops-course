"""Учебная заготовка. Контракт: README.md рядом с файлом."""


def check_prediction_response(payload: dict, expected, model_version: str) -> None:
    # TODO: типы, размер, конечность, численное равенство и версия.
    raise NotImplementedError("Проверь ответ API")


def exercise_api(client, pipeline, batch, model_version: str) -> None:
    # TODO: реальные HTTP запросы через TestClient, assert коды и паритет.
    raise NotImplementedError("Добавь контрактные сценарии API")

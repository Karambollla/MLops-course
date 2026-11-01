"""Учебная заготовка. Контракт: README.md рядом с файлом."""


def resolve_release(client, model_name: str, alias: str, expected_run_id: str) -> dict:
    # TODO: закрепить конкретный номер версии и проверить источник.
    raise NotImplementedError("Разреши alias")


def register_model(
    pipeline, example, run_id: str, model_name: str, tracking_uri: str
) -> dict:
    # TODO: MLflow flavor, signature, aliases, release; lazy import.
    raise NotImplementedError("Зарегистрируй Pipeline")


def assert_parity(original, registered, batch) -> None:
    # TODO: одинаковый batch, конечность и allclose.
    raise NotImplementedError("Сравни registry и bundle")

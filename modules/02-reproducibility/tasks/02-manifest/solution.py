"""Учебная заготовка. Контракт: README.md рядом с файлом."""

from pathlib import Path


def build_manifest(
    data_path: Path, seed: int, split: dict, versions: dict, parameters: dict
) -> dict:
    # TODO: хеш и метаданные, независимая копия split/parameters.
    raise NotImplementedError("Собери манифест")


def validate_bundle(bundle: dict, manifest: dict, expected_sha256: str) -> None:
    # TODO: совместимость до predict, явный ValueError.
    raise NotImplementedError("Проверь контракт bundle")

"""Учебная заготовка. Контракт: README.md рядом с файлом."""

from pathlib import Path


def run_training(
    data_path: str | Path, output_path: str | Path, seed: int = 42
) -> dict:
    # TODO: subprocess ['/opt/housing-venv/bin/python','-m','housing.train',...], check=True.
    # Затем проверить model.joblib/metrics.json/manifest.json/split.json.
    raise NotImplementedError("Вызови настоящее обучение housing.train")

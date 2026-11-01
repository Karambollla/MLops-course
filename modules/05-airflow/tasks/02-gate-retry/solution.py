"""Учебная заготовка. Контракт: README.md рядом с файлом."""

from pathlib import Path


def quality_gate(metrics_path: Path, ratio: float = 0.9) -> bool:
    # TODO: реальные метрики, finite и порог.
    raise NotImplementedError("Реализуй gate")


def publish(
    run_key: str, model_path: Path, version: str, release_dir: Path, metrics_path: Path
) -> dict:
    # TODO: gate до side effect, atomic manifest, идемпотентный ключ.
    raise NotImplementedError("Реализуй публикацию")

"""Учебная заготовка. Контракт: README.md рядом с файлом."""

from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 65536) -> str:
    # TODO: бинарные блоки, без read_bytes для большого файла.
    raise NotImplementedError("Вычисли SHA-256")


def verify_restore(original_hash: str, restored: Path) -> None:
    # TODO: явный отказ при изменённых данных.
    raise NotImplementedError("Проверь восстановление")

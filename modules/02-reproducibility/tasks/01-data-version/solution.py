"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import hashlib
from pathlib import Path

def sha256_file(path: Path, chunk_size: int = 65536) -> str:
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть больше нуля")

    hasher = hashlib.sha256()
    with open(path, "rb") as file:
        while chunk := file.read(chunk_size):
            hasher.update(chunk)

    return hasher.hexdigest()

def verify_restore(original_hash: str, restored: Path) -> None:
    restored_hash = sha256_file(restored)
    if restored_hash != original_hash:
        raise ValueError
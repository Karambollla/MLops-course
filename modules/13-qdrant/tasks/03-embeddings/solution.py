"""Манифест нового индекса; реальную модель установи в отдельное окружение."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import hashlib
import json
import math
from pathlib import Path

try:
    from fastembed import TextEmbedding
except ModuleNotFoundError as exc:
    if exc.name != "fastembed":
        raise
    TextEmbedding = None

try:
    from qdrant_client import QdrantClient, models
except ModuleNotFoundError as exc:
    if exc.name != "qdrant_client":
        raise
    QdrantClient = models = None


def make_manifest(
    model_id: str, revision: str, vectors: list[list[float]], corpus_bytes: bytes
) -> dict:
    raise NotImplementedError("Проверь размерность и происхождение embeddings")

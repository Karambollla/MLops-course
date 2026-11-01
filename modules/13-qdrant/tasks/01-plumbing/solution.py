"""Преобразование корпуса и реальная загрузка в Qdrant."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import json
import math
from pathlib import Path

try:
    from qdrant_client import QdrantClient, models
except ModuleNotFoundError as exc:
    if exc.name != "qdrant_client":
        raise
    QdrantClient = models = None


def build_points(documents: list[dict]) -> list[dict]:
    raise NotImplementedError("Проверь схему и собери points с устойчивыми IDs")


def index_documents(url: str, corpus_path: Path) -> None:
    if QdrantClient is None:
        raise RuntimeError(
            "Install Qdrant SDK: python -m pip install -r labs/qdrant/requirements.txt"
        )
    # TODO: используй QdrantClient и models для коллекции и точек корпуса.
    raise NotImplementedError("Создай коллекцию, выполни upsert и проверь повтор")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:6333")
    parser.add_argument("--corpus", type=Path, default=Path("labs/search/corpus.json"))
    args = parser.parse_args()
    index_documents(args.url, args.corpus)


if __name__ == "__main__":
    main()

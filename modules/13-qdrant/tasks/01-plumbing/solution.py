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


def index_documents(
    url: str, corpus_path: Path, collection: str = "course-docs"
) -> None:
    """Загрузи стабильные IDs в именованную cosine-коллекцию; повтор безопасен.

    До upsert проверь размерность и схему существующей коллекции. Не удаляй
    несовместимую коллекцию: ValueError сохраняет прежние points.
    """
    if QdrantClient is None:
        raise RuntimeError(
            "Install Qdrant SDK: python -m pip install -r labs/qdrant/requirements.txt"
        )
    # TODO: используй QdrantClient и models для коллекции и точек корпуса.
    raise NotImplementedError("Создай коллекцию, выполни upsert и проверь повтор")


def query_documents(
    url: str,
    vector: list[float],
    k: int = 2,
    topic: str | None = None,
    collection: str = "course-docs",
    dimension: int = 4,
) -> list[dict]:
    """query_points(..., with_payload=True).points в порядке ответа Qdrant.

    Верни {id:int, score:float, payload:{text,topic}} для каждого результата.
    topic задаёт models.Filter/FieldCondition/MatchValue внутри query_filter.
    k и dimension — положительные int без bool; vector той же размерности,
    конечный и ненулевой. Неверный ввод — ValueError до SDK; нет hits — [].
    Закрой созданный клиент. Не вычисляй соседей самостоятельно в Python.
    """
    if QdrantClient is None:
        raise RuntimeError(
            "Install SDK: python -m pip install -r labs/qdrant/requirements.txt"
        )
    raise NotImplementedError("Вызови query_points и разбери .points с payload и score")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:6333")
    parser.add_argument("--corpus", type=Path, default=Path("labs/search/corpus.json"))
    parser.add_argument("--collection", default="course-docs")
    parser.add_argument("--action", choices=["index", "query"], default="index")
    parser.add_argument("--vector", type=float, nargs="+", default=[0, 0, 0, 1])
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument("--topic")
    parser.add_argument("--dimension", type=int, default=4)
    args = parser.parse_args()
    if args.action == "index":
        index_documents(args.url, args.corpus, collection=args.collection)
    else:
        result = query_documents(
            args.url, args.vector, args.k, args.topic, args.collection, args.dimension
        )
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

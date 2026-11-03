"""Подготовка NDJSON и проверка bulk items; не путать HTTP200 с успехом всех операций."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import json
from pathlib import Path
import math

try:
    from elasticsearch import Elasticsearch
except ModuleNotFoundError as exc:
    if exc.name != "elasticsearch":
        raise
    Elasticsearch = None


def build_bulk(documents: list[dict], index: str) -> str:
    raise NotImplementedError("Собери пары action/document и стабильные IDs")


def bulk_failures(response: dict) -> list[str]:
    raise NotImplementedError("Проверь каждый item и верни IDs неуспешных действий")


def ensure_index(client, index: str, mapping: dict) -> None:
    """Создай отсутствующий index; существующий проверь на совместимость mapping.

    Нельзя удалять существующий индекс. Несовместимость vector/text/topic или
    vector settings вызывает ValueError до ingest. Повторный вызов безопасен.
    """
    raise NotImplementedError("Используй client.indices.exists/create/get_mapping")


def ingest_documents(client, index: str, documents: list[dict]) -> int:
    """Отправь build_bulk через client.bulk, проверь ВСЕ items, сделай refresh.

    Верни число успешных документов. Частичный отказ: ValueError с IDs из
    bulk_failures; HTTP 200 и errors=False не доказывают успех всех items.
    Повтор с исходными IDs не увеличивает count. Не закрывай переданный client.
    """
    raise NotImplementedError("Выполни реальный bulk, разбор items и refresh")


def lexical_search(
    client, index: str, text: str, k: int = 5, topic: str | None = None
) -> list[dict]:
    """client.search: match text, size=k, optional term topic внутри query.

    Верни ранжированные {id:int, score:float, payload:{text,topic}}.
    k — положительный int без bool, text непустой; иначе ValueError.
    """
    raise NotImplementedError("Отправь lexical query и нормализуй hits.hits")


def vector_search(
    client,
    index: str,
    vector: list[float],
    k: int = 2,
    topic: str | None = None,
    dimension: int = 4,
) -> list[dict]:
    """Отправь нативный kNN с фильтром внутри поиска, не после top-k.

    Формат результата как lexical_search. Проверь положительные целые k и
    dimension без bool, длину, конечность и ненулевую норму до обращения к SDK;
    неверные параметры — ValueError. Для OpenSearch используй knn_request.
    Для Elasticsearch num_candidates >= k (на корпусе достаточно max(8,k)).
    """
    raise NotImplementedError("Отправь kNN через client.search и разбери hits.hits")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["index", "lexical", "vector"])
    parser.add_argument("--url", default="http://127.0.0.1:9200")
    parser.add_argument("--index", default="course-docs")
    parser.add_argument("--corpus", type=Path, default=Path("labs/search/corpus.json"))
    parser.add_argument(
        "--mapping", type=Path, default=Path(__file__).with_name("mapping.json")
    )
    parser.add_argument("--text", default="Vault")
    parser.add_argument("--vector", type=float, nargs="+", default=[0, 0, 0, 1])
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument("--dimension", type=int, default=4)
    parser.add_argument("--topic")
    args = parser.parse_args()
    if Elasticsearch is None:
        parser.error(
            "Install SDKs: python -m pip install -r labs/search/requirements.txt"
        )
    client = Elasticsearch(args.url)
    try:
        if args.action == "index":
            mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
            documents = json.loads(args.corpus.read_text(encoding="utf-8"))
            ensure_index(client, args.index, mapping)
            result = ingest_documents(client, args.index, documents)
        elif args.action == "lexical":
            result = lexical_search(client, args.index, args.text, args.k, args.topic)
        else:
            result = vector_search(
                client, args.index, args.vector, args.k, args.topic, args.dimension
            )
        print(json.dumps(result, ensure_ascii=False))
    finally:
        client.close()


if __name__ == "__main__":
    main()

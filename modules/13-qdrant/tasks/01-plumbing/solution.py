"""Преобразование корпуса и реальная загрузка в Qdrant."""

import argparse
from pathlib import Path


def build_points(documents: list[dict]) -> list[dict]:
    raise NotImplementedError("Проверь схему и собери points с устойчивыми IDs")


def index_documents(url: str, corpus_path: Path) -> None:
    # SDK qdrant_client нужен только для реального подключения; импортируй его здесь.
    raise NotImplementedError("Создай коллекцию, выполни upsert и проверь повтор")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:6333")
    parser.add_argument("--corpus", type=Path, default=Path("labs/search/corpus.json"))
    args = parser.parse_args()
    index_documents(args.url, args.corpus)


if __name__ == "__main__":
    main()

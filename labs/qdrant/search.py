"""Упражнение 13: сначала ручные векторы из corpus.json и queries.json, затем собственные embeddings."""
import json
from pathlib import Path
from qdrant_client import QdrantClient

client = QdrantClient(url="http://127.0.0.1:6333")
corpus = json.loads(Path("labs/search/corpus.json").read_text(encoding="utf-8"))
# TODO(student): create collection(dim=4, cosine), stable integer IDs, upsert, query_points.
raise NotImplementedError("Загрузи корпус и реализуй поиск с фильтром")

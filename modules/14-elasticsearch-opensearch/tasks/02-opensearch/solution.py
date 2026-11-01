"""Контракт OpenSearch kNN; размерность передавай из версии индекса."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import json
import math
from urllib.request import Request, urlopen


def knn_request(
    vector: list[float], k: int, topic: str | None = None, dimension: int = 4
) -> dict:
    raise NotImplementedError("Собери kNN query с проверкой размера и фильтром")

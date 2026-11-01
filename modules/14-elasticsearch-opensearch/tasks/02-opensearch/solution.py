"""Контракт OpenSearch kNN; размерность передавай из версии индекса."""


def knn_request(
    vector: list[float], k: int, topic: str | None = None, dimension: int = 4
) -> dict:
    raise NotImplementedError("Собери kNN query с проверкой размера и фильтром")

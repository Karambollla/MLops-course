"""Манифест нового индекса; реальную модель установи в отдельное окружение."""


def make_manifest(
    model_id: str, revision: str, vectors: list[list[float]], corpus_bytes: bytes
) -> dict:
    raise NotImplementedError("Проверь размерность и происхождение embeddings")

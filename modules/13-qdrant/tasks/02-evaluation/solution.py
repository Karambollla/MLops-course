"""Метрики ранжирования; вычисляй их по независимым qrels."""


def ranking_metrics(retrieved: list, relevant: list, k: int) -> dict[str, float]:
    raise NotImplementedError("Вычисли recall, precision и reciprocal rank")

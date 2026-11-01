"""Измерение клиентского streaming; timestamps берутся monotonic clock."""


def request_metrics(
    started: float, events: list[dict], ended: float, output_tokens: int
) -> dict:
    raise NotImplementedError(
        "Найди первый непустой content и вычисли объявленные метрики"
    )

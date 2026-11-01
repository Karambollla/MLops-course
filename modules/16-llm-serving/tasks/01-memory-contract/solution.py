"""CPU-задание: оценки памяти и обработка протокола без фиктивного LLM runtime."""


def weights_bytes(parameters: int, bytes_per_parameter: int = 2) -> int:
    raise NotImplementedError("Оцени размер весов и проверь вход")


def kv_cache_bytes(
    layers: int,
    kv_heads: int,
    head_dim: int,
    context: int,
    concurrency: int,
    bytes_per_element: int = 2,
) -> int:
    raise NotImplementedError(
        "Оцени key/value cache без подмены kv_heads числом query heads"
    )


def sse_contents(lines: list[str]) -> list[str]:
    raise NotImplementedError(
        "Разбери data events, первый полезный content, DONE и ошибки"
    )

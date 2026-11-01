"""Подготовка NDJSON и проверка bulk items; не путать HTTP200 с успехом всех операций."""


def build_bulk(documents: list[dict], index: str) -> str:
    raise NotImplementedError("Собери пары action/document и стабильные IDs")


def bulk_failures(response: dict) -> list[str]:
    raise NotImplementedError("Проверь каждый item и верни IDs неуспешных действий")

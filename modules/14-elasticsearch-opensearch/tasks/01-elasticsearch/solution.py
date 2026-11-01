"""Подготовка NDJSON и проверка bulk items; не путать HTTP200 с успехом всех операций."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import json
import math
from urllib.request import Request, urlopen


def build_bulk(documents: list[dict], index: str) -> str:
    raise NotImplementedError("Собери пары action/document и стабильные IDs")


def bulk_failures(response: dict) -> list[str]:
    raise NotImplementedError("Проверь каждый item и верни IDs неуспешных действий")

"""Необязательный автоматический сбор реальных read-only свидетельств.
Можно заполнить evidence.json вручную, сохранив вывод Docker/HTTP в report.md.
"""

from pathlib import Path


def collect_evidence(container_id: str, base_url: str, request_path: Path) -> dict:
    # TODO: docker inspect/image inspect/exec pip freeze (без изменения контейнера),
    # HTTP GET /ready и POST /predict; возврат по схеме evidence.json.
    # subprocess только с массивом аргументов и check=True, сеть внутри функции.
    raise NotImplementedError(
        "Собери фактические свидетельства или заполни evidence.json вручную"
    )

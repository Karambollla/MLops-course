"""Vault: минимальные права — учебная заготовка. Импорт не обращается к инфраструктуре."""

import argparse
import json
import os
from urllib.request import Request, urlopen


def inspect_payload(payload):
    """Проверь наличие ключа без возврата/вывода секрета."""
    # TODO(student): реализуй контракт из README и тестов.
    raise NotImplementedError("inspect_payload")


def main():
    """HTTP-обвязка; обработку payload и отказов реализуй по условиям задания."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--address", default=os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    )
    args = parser.parse_args()
    token = os.environ["VAULT_TOKEN"]
    request = Request(
        args.address + "/v1/secret/data/housing", headers={"X-Vault-Token": token}
    )
    with urlopen(request, timeout=5) as response:
        payload = json.load(response)
    print(json.dumps(inspect_payload(payload), ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Упражнение 10: прочитать KV v2 с ограниченным токеном, не печатать секрет."""
import os
import json
from urllib.request import Request, urlopen

def main():
    address = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
    token = os.environ["VAULT_TOKEN"]
    request = Request(address + "/v1/secret/data/housing", headers={"X-Vault-Token": token})
    with urlopen(request, timeout=5) as response:
        payload = json.load(response)
    # TODO(student): use payload["data"]["data"] without logging secrets; handle expiry.
    raise NotImplementedError("Подключи секрет и обработку 403, не выводи значение")

if __name__ == "__main__":
    main()

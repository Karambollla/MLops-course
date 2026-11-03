"""Vault KV v2: SDK-обвязка и учебные функции без раскрытия секрета."""

import argparse
import json
import os

try:
    import hvac
    from requests.exceptions import Timeout
except ModuleNotFoundError as exc:
    if exc.name != "hvac":
        raise
    hvac = None


def inspect_payload(payload):
    """Проверь наличие ключа без возврата/вывода секрета."""
    raise NotImplementedError("inspect_payload")


def read_secret(client, path="housing", mount_point="secret") -> dict:
    """Прочитай KV v2 через SDK и верни только результат inspect_payload."""
    # TODO(student): client.secrets.kv.v2.read_secret_version + inspect_payload.
    # Forbidden/Timeout должны дойти до вызывающего кода без retry/печати payload.
    raise NotImplementedError("read_secret: реализуй чтение через hvac KV v2")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--address", default=os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    )
    parser.add_argument("--path", default="housing")
    parser.add_argument("--mount", default="secret")
    parser.add_argument("--timeout", type=float, default=5)
    args = parser.parse_args()
    if hvac is None:
        raise RuntimeError(
            "Install SDK: python -m pip install -r labs/vault/requirements.txt"
        )
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    client = hvac.Client(
        url=args.address, token=os.environ["VAULT_TOKEN"], timeout=args.timeout
    )
    try:
        result = read_secret(client, path=args.path, mount_point=args.mount)
    except hvac.exceptions.Forbidden:
        parser.exit(1, "access_denied\n")
    except hvac.exceptions.VaultError:
        parser.exit(1, "vault_error\n")
    except Timeout:
        parser.exit(1, "network_timeout\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Классификация отказов и жизненный цикл собственного временного token."""

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


def classify_error(status=None, timeout=False):
    """Раздели истечение прав и сетевую недоступность без бесконечного retry."""
    raise NotImplementedError("classify_error")


def renew_token(client, increment="60s") -> dict:
    """Продли только token текущего client; результат: ttl_seconds и renewable."""
    # TODO(student): auth.token.renew_self; не возвращай auth/client_token.
    raise NotImplementedError("renew_token: используй hvac auth.token.renew_self")


def revoke_token(client) -> dict:
    """Отзови только собственный token; верни {revoked: True}."""
    # TODO(student): auth.token.revoke_self; не принимай чужой token аргументом.
    raise NotImplementedError("revoke_token: используй hvac auth.token.revoke_self")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["renew", "revoke"])
    parser.add_argument(
        "--address", default=os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    )
    parser.add_argument("--increment", default="60s")
    args = parser.parse_args()
    if hvac is None:
        raise RuntimeError(
            "Install SDK: python -m pip install -r labs/vault/requirements.txt"
        )
    client = hvac.Client(url=args.address, token=os.environ["VAULT_TOKEN"], timeout=5)
    try:
        if args.action == "renew":
            result = renew_token(client, increment=args.increment)
        else:
            result = revoke_token(client)
    except hvac.exceptions.Forbidden:
        parser.exit(1, "access_denied\n")
    except hvac.exceptions.VaultError:
        parser.exit(1, "vault_error\n")
    except Timeout:
        parser.exit(1, "network_timeout\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

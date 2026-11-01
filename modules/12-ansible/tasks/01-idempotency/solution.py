"""Разбор результатов собственной Ansible-практики."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import json
import re
from pathlib import Path


def parse_recap(text: str) -> dict[str, dict[str, int]]:
    raise NotImplementedError("Разбери PLAY RECAP и проверь числовые поля")


def compare_runs(first: str, second: str) -> dict:
    raise NotImplementedError(
        "Проверь одинаковые hosts, отсутствие ошибок и changed=0 при повторе"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            compare_runs(args.first.read_text(), args.second.read_text()),
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

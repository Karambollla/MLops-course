"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import json
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
import json
from course_tasks import load_task

def validate(stream: dict) -> bool:
    return isinstance(stream, dict) and len(stream) > 0 and stream["duration"] > 0 and isinstance(stream["duration"], int | float)

def iter_records(stream: Iterable[str]) -> Iterator[dict]:
    for i, js in enumerate(stream, start=1):
        try:
            js = json.loads(js)
        except:
            raise ValueError(f"Invalid JSON on line {i}")        
        if not isinstance(js, dict):
            raise ValueError(f"Invalid JSON on line {i}")
        yield js

def summarize_file(path: Path) -> dict:
    summarize = load_task('00-python/01-records').summarize
    with open(path, "r") as file:
        iterator = iter_records(file)
        result = summarize(iterator)
    return result


def main() -> None:
    # TODO: argparse, stdout JSON, stderr и exit != 0 при ошибке.
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    try:
        result = summarize_file(args.path)
    except (ValueError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main()

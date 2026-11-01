"""Собственные наблюдения; основная заготовка — playbook.yaml и report.json."""

import argparse
import json
from pathlib import Path


def collect_report() -> dict:
    raise NotImplementedError(
        "Собери реальные выводы трёх запусков без изменения ресурсов"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(json.loads(args.report.read_text()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Учебная заготовка. Контракт: README.md рядом с файлом."""

import argparse
import os
from pathlib import Path


def select_candidate(runs: list[dict]) -> str:
    # TODO: проверка сопоставимости и выбор только по validation.
    raise NotImplementedError("Выбери run")


def track_experiments(data: Path, output: Path, tracking_uri: str) -> list[dict]:
    # TODO: lazy mlflow import, реальный train и logging.
    raise NotImplementedError("Залогируй три эксперимента")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("work/housing.csv"))
    parser.add_argument("--output", type=Path, default=Path("work/mlflow-runs"))
    parser.add_argument(
        "--tracking-uri",
        default=os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"),
    )
    args = parser.parse_args()
    track_experiments(args.data, args.output, args.tracking_uri)


if __name__ == "__main__":
    main()

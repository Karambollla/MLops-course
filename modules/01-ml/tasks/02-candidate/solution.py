"""Учебная заготовка. Контракт: README.md рядом с файлом."""

import argparse
from pathlib import Path

from sklearn.pipeline import Pipeline


def build_pipeline(seed: int = 42) -> "Pipeline":
    # TODO: preprocessing и estimator из обязательного scikit-learn.
    raise NotImplementedError("Создай Pipeline")


def train(data: Path, output: Path, seed: int) -> None:
    # TODO: load_task('01-ml/01-baseline'), сравнение и артефакты.
    raise NotImplementedError("Реализуй обучение")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    train(args.data, args.output, args.seed)


if __name__ == "__main__":
    main()

"""Совместимый CLI: реализация находится в modules/01-ml/tasks/02-candidate/solution.py."""

from pathlib import Path

from sklearn.pipeline import Pipeline
from course_tasks import load_task


def build_pipeline(seed: int = 42) -> Pipeline:
    return load_task("01-ml/02-candidate").build_pipeline(seed)


def train(data: Path, output: Path, seed: int) -> None:
    return load_task("01-ml/02-candidate").train(data, output, seed)


def main() -> None:
    return load_task("01-ml/02-candidate").main()


if __name__ == "__main__":
    main()

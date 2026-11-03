"""CLI обучения: определения берутся из сохранённого modules/01-ml/housing.ipynb."""

from pathlib import Path

from sklearn.pipeline import Pipeline
from course_tasks.notebook import housing_notebook_path, load_notebook


def build_pipeline(seed: int = 42) -> Pipeline:
    return load_notebook(housing_notebook_path()).build_pipeline(seed)


def train(data: Path, output: Path, seed: int) -> None:
    return load_notebook(housing_notebook_path()).train(data, output, seed)


def main() -> None:
    return load_notebook(housing_notebook_path()).main()


if __name__ == "__main__":
    main()

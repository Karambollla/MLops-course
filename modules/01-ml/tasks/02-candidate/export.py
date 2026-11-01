"""Готовый перенос комплекта обучения; solution.py не выполняется."""

from pathlib import Path

from course_tasks import course_root
from course_tasks.artifacts import export_cli


def main():
    task = Path(__file__).resolve().parent
    destination = course_root() / "work" / "artifacts"
    # Модель заменяется последней, после метаданных.
    names = ["metrics.json", "manifest.json", "split.json", "model.joblib"]
    export_cli(
        [(task / "output" / name, destination / name) for name in names], service="API"
    )


if __name__ == "__main__":
    main()

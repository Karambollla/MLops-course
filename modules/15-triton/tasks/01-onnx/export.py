"""Готовый перенос ONNX и config; решение и Triton не запускаются."""

from pathlib import Path

from course_tasks import course_root
from course_tasks.artifacts import export_cli


def main():
    task = Path(__file__).resolve().parent
    destination = course_root() / "work" / "triton" / "model_repository" / "housing"
    export_cli(
        [
            (task / "config.pbtxt", destination / "config.pbtxt"),
            (task / "output" / "model.onnx", destination / "1" / "model.onnx"),
        ],
        service="Triton",
    )


if __name__ == "__main__":
    main()

"""Student ClearML integration. Importing does not require the SDK."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import json
import os
from pathlib import Path

import housing.train

try:
    from clearml import Task
except ModuleNotFoundError as exc:
    if exc.name != "clearml":
        raise
    Task = None


def train_and_log(task, data_path: Path, output_dir: Path, seed: int = 42):
    """Train housing, connect provenance, log test metrics and upload real artifacts."""
    # TODO(student): call housing.train.train and use its actual output files.
    raise NotImplementedError("train_and_log")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if Task is None:
        raise RuntimeError(
            "Install ClearML SDK: python -m pip install -r labs/clearml/requirements.txt"
        )

    Task.set_offline(
        offline_mode=Task.running_locally()
        and os.getenv("CLEARML_OFFLINE_MODE", "1") == "1"
    )
    task = Task.init(project_name="mlops-course", task_name="housing-student")
    try:
        return train_and_log(task, args.data, args.output, args.seed)
    finally:
        task.close()


if __name__ == "__main__":
    main()

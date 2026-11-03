#!/usr/bin/env python3
"""List technical exercises and guides, or run explicit task checks."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from course_tasks import course_root, task_catalog, task_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Задания курса MLOps")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Показать идентификаторы всех заданий")
    test = commands.add_parser(
        "test", help="Проверить одно задание или все учебные задания"
    )
    test.add_argument("task", nargs="?")
    test.add_argument("--all", action="store_true")
    run = commands.add_parser(
        "run", help="Запустить Python-заготовку выбранного задания"
    )
    run.add_argument("task")
    arguments = sys.argv[1:]
    if "--" in arguments:
        separator = arguments.index("--")
        args = parser.parse_args(arguments[:separator])
        extra = arguments[separator + 1 :]
    else:
        args, extra = parser.parse_known_args(arguments)
    try:
        root = course_root()
        catalog = task_catalog()
        if args.command == "list":
            if extra:
                parser.error("У list нет дополнительных аргументов")
            for task in catalog:
                kind = (
                    "руководство"
                    if task.get("kind") == "guide"
                    else "стенд"
                    if task.get("kind") == "integration"
                    else "код"
                )
                print(f"{task['id']}  [{kind}] {task['title']}")
            print(
                "01-ml: задания и проверки находятся в modules/01-ml/housing.ipynb; запускай ячейки notebook."
            )
            return 0
        if args.command == "test":
            print(
                "01-ml пропущен: проверки запускаются внутри modules/01-ml/housing.ipynb.",
                flush=True,
            )
            if args.all and args.task:
                parser.error("Выбери одно задание либо --all")
            if not args.task and not args.all:
                parser.error("Укажи задание: make task TASK=00-python/01-records")
            selected = (
                catalog
                if args.all
                else [task for task in catalog if task["id"] == args.task]
            )
            if not selected:
                task_directory(
                    args.task
                )  # Produce the same clear validation error as the loader.
            if not args.all and selected[0].get("kind") == "guide":
                print(
                    f"Руководство с примерами; автоматических проверок нет: {task_directory(args.task) / 'README.md'}"
                )
                return 0
            selected = [
                task
                for task in selected
                if task.get("tests", "test_task.py") is not None
            ]
            if not selected:
                print("Автоматических проверок нет; открой README материалов.")
                return 0
            paths = [
                str(
                    task_directory(task["id"])
                    if task.get("tests", "test_task.py") == "test_task.py"
                    else task_directory(task["id"]) / task["tests"]
                )
                for task in selected
            ]
            command = [
                sys.executable,
                "-m",
                "pytest",
                "--import-mode=importlib",
                "--rootdir",
                str(root),
                *paths,
                *extra,
            ]
            result = subprocess.run(command, cwd=root)
            return result.returncode
        directory = task_directory(args.task)
        task = next(task for task in catalog if task["id"] == args.task)
        if task.get("kind") == "guide":
            print(
                f"Руководство с примерами; автоматических проверок нет: {directory / 'README.md'}"
            )
            return 0
        entrypoint = task.get("entrypoint", task.get("starter", "solution.py"))
        if entrypoint is None:
            parser.error(
                "У этого задания нет CLI: реализуй функции и запусти make task TASK="
                + args.task
            )
        entry = (directory / entrypoint).resolve()
        if not entry.is_relative_to(directory) or entry.suffix != ".py":
            parser.error(
                "У этого задания заготовка конфигурации. Открой его README для команды запуска."
            )
        if not entry.is_file():
            raise FileNotFoundError(f"Нет Python-заготовки: {entry}")
        environment = os.environ.copy()
        environment["MLOPS_COURSE_ROOT"] = str(root)
        return subprocess.run(
            [sys.executable, str(entry), *extra], cwd=root, env=environment
        ).returncode
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())

"""Сбор собственных наблюдений; основной артефакт задания — report.json."""

import argparse
import json
from pathlib import Path


def collect_report():
    """TODO: собери обезличенные реальные наблюдения read-only запросами/выводом CLI.

    Верни dict по report.template.json. Не создавай/не удаляй ресурсы в этой функции.
    Основной workflow выполняется студентом явно по README. Допустимо заполнить
    report.json вручную; реализовывать grader не требуется.
    """
    raise NotImplementedError("Собери собственные наблюдения")


def main():
    """--report PATH выводит собственный отчёт; --collect собирает и выводит его."""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report")
    group.add_argument("--collect", action="store_true")
    args = parser.parse_args()
    report = (
        collect_report() if args.collect else json.loads(Path(args.report).read_text())
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

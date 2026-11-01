"""Мониторинг: качество и drift — учебная заготовка. Импорт не обращается к инфраструктуре."""

import argparse
import json
from pathlib import Path


def analyze(targets, predictions, reference_medinc, shifted_medinc):
    """Совмести predictions/targets по ID; рассчитай MAE и квантили распределений."""
    # TODO(student): реализуй контракт из README и тестов.
    raise NotImplementedError("analyze")


def main():
    """CLI: --report PATH; вывод наблюдений. Проверка отчёта — test_task.py."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    result = json.loads(Path(args.report).read_text())
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

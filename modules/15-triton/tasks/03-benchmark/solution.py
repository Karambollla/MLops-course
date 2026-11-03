"""Показатели клиента: throughput считается по стенному времени, не сумме latency."""

# ruff: noqa: F401
# SDK/численные импорты подготовлены для student-реализации.

import argparse
import json
import os
from pathlib import Path
from time import perf_counter

import numpy as np
from course_tasks import load_task
from housing.features import FEATURES


def latency_summary(
    rows: list[dict], elapsed_seconds: float, min_requests: int = 200
) -> dict:
    raise NotImplementedError("Проверь измерения и вычисли latency/throughput/errors")


def benchmark(
    client,
    rows: list[dict],
    feature_order: list[str],
    requests=200,
    warmup=5,
    model_name="housing",
    output_names=("variable",),
) -> dict:
    """Измерь последовательную серию student infer; верни rows и elapsed_seconds."""
    # TODO(student): load_task('15-triton/02-server').infer, perf_counter.
    # warmup исключён из samples/wall time; ошибки учитываются без текста ответа.
    raise NotImplementedError(
        "benchmark: измерь реальные SDK-вызовы, не генерируй latency"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", required=True, type=Path)
    parser.add_argument(
        "--url", default=os.getenv("TRITON_URL", "http://127.0.0.1:8000")
    )
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument(
        "--output", required=True, type=Path, help="Raw measurements and summary JSON"
    )
    args = parser.parse_args()
    if args.requests < 200 or args.warmup < 0:
        parser.error("--requests must be >=200 and --warmup >=0")
    server = load_task("15-triton/02-server")
    rows = json.loads(args.rows.read_text(encoding="utf-8"))
    with server.create_client(args.url) as client:
        measured = benchmark(
            client, rows, list(FEATURES), requests=args.requests, warmup=args.warmup
        )
    result = {
        **measured,
        "summary": latency_summary(measured["rows"], measured["elapsed_seconds"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"], allow_nan=False))


if __name__ == "__main__":
    main()

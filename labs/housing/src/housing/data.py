"""Загрузчик данных; это инфраструктура, а не решение обучения."""
import argparse
import hashlib
from pathlib import Path
from sklearn.datasets import fetch_california_housing
from housing.features import FEATURES, TARGET


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Файл уже существует: сохрани версию или укажи новый путь")
    dataset = fetch_california_housing(as_frame=True, data_home=args.output.parent / ".dataset-cache")
    frame = dataset.frame[FEATURES + [TARGET]]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False, float_format="%.12g")
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix(".sha256").write_text(digest + "\n", encoding="utf-8")
    print(f"rows={len(frame)} columns={len(frame.columns)} sha256={digest}")


if __name__ == "__main__":
    main()

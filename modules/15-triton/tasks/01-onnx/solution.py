"""Экспортируется собственный Pipeline; заготовка не содержит готовой модели."""

import argparse
from pathlib import Path

import numpy as np


def feature_matrix(rows: list[dict], feature_order: list[str]) -> np.ndarray:
    raise NotImplementedError(
        "Проверь поля и построй float32 матрицу в каноническом порядке"
    )


def parity(expected, observed, rtol=1e-4, atol=1e-5) -> dict:
    raise NotImplementedError("Проверь размерность, конечность и численное совпадение")


def export_bundle(bundle_path: Path, output_path: Path) -> None:
    # skl2onnx/onnxruntime — необязательные SDK; импорт нужен при выполнении экспорта.
    raise NotImplementedError(
        "Экспортируй Pipeline и проверь 100 строк через ONNX Runtime"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bundle", type=Path, default=Path("work/artifacts/model.joblib")
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("labs/triton/model_repository/housing/1/model.onnx"),
    )
    args = parser.parse_args()
    export_bundle(args.bundle, args.output)


if __name__ == "__main__":
    main()

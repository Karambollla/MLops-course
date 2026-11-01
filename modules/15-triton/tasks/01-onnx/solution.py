"""Экспортируется собственный Pipeline; заготовка не содержит готовой модели."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from housing.features import FEATURES

try:
    import onnx
    import onnxruntime as ort
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
except ModuleNotFoundError as exc:
    if exc.name not in {"onnx", "onnxruntime", "skl2onnx"}:
        raise
    onnx = ort = convert_sklearn = FloatTensorType = None


def feature_matrix(rows: list[dict], feature_order: list[str]) -> np.ndarray:
    raise NotImplementedError(
        "Проверь поля и построй float32 матрицу в каноническом порядке"
    )


def parity(expected, observed, rtol=1e-4, atol=1e-5) -> dict:
    raise NotImplementedError("Проверь размерность, конечность и численное совпадение")


def export_bundle(bundle_path: Path, output_path: Path) -> None:
    if any(
        dependency is None
        for dependency in (onnx, ort, convert_sklearn, FloatTensorType)
    ):
        raise RuntimeError(
            "Install ONNX export dependencies: python -m pip install -r labs/triton/requirements.txt"
        )
    # TODO: используй convert_sklearn / FloatTensorType, onnx.checker и ort.
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
        default=Path(__file__).resolve().parent / "output" / "model.onnx",
    )
    args = parser.parse_args()
    export_bundle(args.bundle, args.output)


if __name__ == "__main__":
    main()

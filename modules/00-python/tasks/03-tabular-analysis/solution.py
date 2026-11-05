"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

from pathlib import Path

import pandas as pd
from scipy import stats

def describe_frame(frame: pd.DataFrame) -> dict:
    quantiles = frame.quantile([0.25, 0.5, 0.75], numeric_only=True)
    quantiles.index = quantiles.index.map(str)

    return {
        "shape": list([len(frame), len(frame.columns)]),
        "dtypes": frame.dtypes.to_dict(),
        "missing": frame.isna().sum().to_dict(),
        "quantiles": quantiles.to_dict()
    }


def align_series(left: pd.Series, right: pd.Series) -> tuple:
    common = left.index.intersection(right.index, sort=False)
    return left[common], right[common]

def write_report(csv_path: Path, output: Path) -> None:
    frame = pd.read_csv(csv_path)
    summary = describe_frame(frame)

    output.parent.mkdir(parents=True, exist_ok=True)

    report = "# Сводка данных\n\n"
    for name, value in summary.items():
        report += f"## {name}\n\n{value}\n\n"

    output.write_text(report, encoding="utf-8")
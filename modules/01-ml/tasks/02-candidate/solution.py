"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import argparse
import hashlib
import json
import os
import platform
import tempfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from course_tasks import load_task
from housing.features import FEATURES, TARGET


def build_pipeline(seed: int = 42) -> "Pipeline":
    # TODO: preprocessing и estimator из обязательного scikit-learn.
    raise NotImplementedError("Создай Pipeline")


def train(data: Path, output: Path, seed: int) -> None:
    # TODO: load_task('01-ml/01-baseline'), сравнение и артефакты.
    raise NotImplementedError("Реализуй обучение")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    train(args.data, args.output, args.seed)


if __name__ == "__main__":
    main()

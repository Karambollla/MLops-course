"""Упражнения 01–02.

CLI обязан создать model.joblib, metrics.json, manifest.json, split.json.
Bundle: {schema_version: 1, pipeline: fitted estimator, features: FEATURES,
         model_version: nonempty str}.
metrics.json: baseline и candidate, у каждого validation/test с mae/rmse.
manifest.json: seed, data_sha256, versions, parameters, feature_order, split.
split.json: train/validation/test со списками исходных индексов строк.
Pipeline принимает DataFrame с восемью столбцами; target в него не входит.
"""
import argparse
from pathlib import Path
from sklearn.pipeline import Pipeline


def build_pipeline(seed: int = 42) -> Pipeline:
    # TODO(student): выбери preprocessing и estimator из модуля 01.
    raise NotImplementedError("Создай sklearn Pipeline")


def train(data: Path, output: Path, seed: int) -> None:
    # TODO(student): split, baseline, evaluation, bundle, atomic publication.
    raise NotImplementedError("Реализуй цикл обучения и сохранение артефактов")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    train(args.data, args.output, args.seed)


if __name__ == "__main__":
    main()

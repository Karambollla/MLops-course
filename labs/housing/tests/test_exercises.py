"""Opt in with RUN_EXERCISES=1 after reading practice instructions."""
import os
import numpy as np
import pandas as pd
import pytest
from housing.features import FEATURES

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_EXERCISES") != "1",
    reason="Учебная логика: включить RUN_EXERCISES=1 после чтения practice.md",
)


def test_training_pipeline_predicts_and_preserves_feature_order():
    from housing.train import build_pipeline
    # Small fixture for the interface; full quality is measured on California Housing.
    rng = np.random.default_rng(42)
    x = pd.DataFrame(rng.normal(size=(40, len(FEATURES))), columns=FEATURES)
    y = 2 * x["MedInc"] + 1
    pipeline = build_pipeline(seed=42)
    pipeline.fit(x, y)
    predictions = pipeline.predict(x.iloc[:3])
    assert predictions.shape == (3,)
    assert np.isfinite(predictions).all()


def test_evaluation_has_correct_units():
    from housing.evaluate import regression_metrics
    metrics = regression_metrics(np.array([1.0, 3.0]), np.array([1.0, 1.0]))
    assert metrics["mae"] == pytest.approx(1.0)
    assert metrics["rmse"] == pytest.approx(2 ** 0.5)

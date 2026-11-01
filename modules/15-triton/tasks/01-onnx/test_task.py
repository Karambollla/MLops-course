import os
from importlib.metadata import version

import joblib
import pandas as pd
from housing.features import FEATURES, TARGET
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import numpy as np
import pytest
from course_tasks import load_solution

try:
    import onnx
    import onnxruntime as ort
    import skl2onnx
except ModuleNotFoundError as exc:
    if exc.name not in {"onnx", "onnxruntime", "skl2onnx"}:
        raise
    onnx = ort = skl2onnx = None

s = load_solution(__file__)


def test_feature_order_is_restored_before_float32_export():
    actual = s.feature_matrix([{"b": 2.0, "a": 1.0}], ["a", "b"])
    assert actual.dtype == np.float32 and actual.shape == (1, 2)
    np.testing.assert_array_equal(actual, [[1, 2]])


@pytest.mark.parametrize(
    "rows",
    [
        [{"a": 1}],
        [{"a": True, "b": 2}],
        [{"a": float("inf"), "b": 2}],
        [{"a": 1, "b": 2, "target": 3}],
    ],
)
def test_bad_model_input_is_rejected(rows):
    with pytest.raises(ValueError):
        s.feature_matrix(rows, ["a", "b"])


def test_onnx_vector_shape_and_tolerance():
    result = s.parity(np.array([1.0, 2.0]), np.array([[1.0], [2.000001]]))
    assert result["passed"] is True
    assert result["max_abs_error"] == pytest.approx(0.000001)
    assert s.parity([1.0], [1.5])["passed"] is False
    with pytest.raises(ValueError):
        s.parity([1.0], [float("nan")])


def test_multiple_rows_restore_feature_order_independent_of_key_order():
    rows = [{"b": 4, "a": 3}, {"a": -1, "b": 0.5}, {"b": 8, "a": 2}]
    actual = s.feature_matrix(rows, ["a", "b"])
    assert actual.dtype == np.float32
    np.testing.assert_array_equal(actual, [[3, 4], [-1, 0.5], [2, 8]])
    assert actual.shape == (3, 2)
    reordered = [dict(reversed(list(row.items()))) for row in rows]
    np.testing.assert_array_equal(s.feature_matrix(reordered, ["a", "b"]), actual)


@pytest.mark.parametrize("bad", [float("nan"), -float("inf"), "number"])
def test_nonfinite_and_nonnumeric_feature_values(bad):
    with pytest.raises(ValueError):
        s.feature_matrix([{"a": 1, "b": 2}, {"a": bad, "b": 3}], ["a", "b"])


@pytest.mark.parametrize(
    "expected,observed",
    [
        ([1, 2], [[1], [2]]),
        ([[1], [2]], [1, 2]),
        ([[1], [2]], [[1], [2]]),
        ([1, 2], [1, 2]),
    ],
)
def test_parity_accepts_vector_and_column_in_either_order(expected, observed):
    assert s.parity(expected, observed) == {"passed": True, "max_abs_error": 0}


@pytest.mark.parametrize(
    "expected,observed",
    [
        ([1, 2], [1]),
        ([[1, 2]], [1, 2]),
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([float("inf")], [1]),
        ([1], [-float("inf")]),
        ([float("nan")], [1]),
    ],
)
def test_parity_rejects_broadcastable_shapes_and_nonfinite_values(expected, observed):
    with pytest.raises(ValueError):
        s.parity(expected, observed)


def test_parity_reports_maximum_difference_and_uses_requested_tolerance():
    result = s.parity([1, 2, 3], [1.01, 2.03, 3.02], rtol=0, atol=0.04)
    assert result["passed"] is True
    assert result["max_abs_error"] == pytest.approx(0.03)
    result = s.parity([1, 2, 3], [1.01, 2.03, 3.02], rtol=0, atol=0.02)
    assert result["passed"] is False
    assert result["max_abs_error"] == pytest.approx(0.03)
    assert s.parity([1000], [1000.5], rtol=0.001, atol=0)["passed"] is True


@pytest.mark.sdk
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_SDK") != "1",
    reason="Set MLOPS_RUN_SDK=1 for local ONNX export",
)
def test_sdk_export_bundle_preserves_synthetic_pipeline_predictions(
    tmp_path, monkeypatch
):
    assert all(module is not None for module in (onnx, ort, skl2onnx)), (
        "MLOPS_RUN_SDK=1 requires python -m pip install -r labs/triton/requirements.txt "
        "and python -m pip install --no-deps -e labs/housing"
    )
    for distribution, pinned in [
        ("onnx", "1.17.0"),
        ("skl2onnx", "1.18.0"),
        ("onnxruntime", "1.22.0"),
    ]:
        assert version(distribution) == pinned, "Install labs/triton/requirements.txt"
    rng = np.random.default_rng(17)
    values = rng.normal(size=(100, len(FEATURES))).astype(np.float32)
    frame = pd.DataFrame(values, columns=FEATURES)
    target = values @ np.array([0.4, -0.2, 0.8, 0.1, -0.3, 0.6, 0.2, -0.5]) + 2
    pipeline = Pipeline(
        [("scale", StandardScaler()), ("regressor", LinearRegression())]
    )
    pipeline.fit(frame, target)
    bundle = {
        "schema_version": 1,
        "features": list(FEATURES),
        "pipeline": pipeline,
        "model_version": "synthetic-sdk-test",
    }
    bundle_path = tmp_path / "model.joblib"
    joblib.dump(bundle, bundle_path)
    # Accommodate exporters that read the documented default validation CSV.
    work = tmp_path / "work"
    work.mkdir()
    frame.assign(**{TARGET: target}).to_csv(work / "housing.csv", index=False)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "nested" / "onnx" / "model.onnx"
    s.export_bundle(bundle_path, output)
    assert output.is_file() and output.stat().st_size > 0
    graph = onnx.load(str(output))
    onnx.checker.check_model(graph)
    assert any(
        item.domain in ("", "ai.onnx") and item.version == 17
        for item in graph.opset_import
    )
    session = ort.InferenceSession(str(output), providers=["CPUExecutionProvider"])
    inputs = session.get_inputs()
    assert len(inputs) == 1
    assert inputs[0].name == "features" and inputs[0].type == "tensor(float)"
    assert len(inputs[0].shape) == 2 and inputs[0].shape[1] == 8
    assert not isinstance(inputs[0].shape[0], int)
    observed = session.run(None, {"features": values})
    assert len(observed) == 1
    actual = np.asarray(observed[0])
    assert actual.shape in {(100,), (100, 1)}
    assert np.isfinite(actual).all()
    expected = pipeline.predict(frame)
    np.testing.assert_allclose(actual.reshape(-1), expected, rtol=1e-4, atol=1e-5)

import numpy as np
import pytest
from course_tasks import load_solution

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

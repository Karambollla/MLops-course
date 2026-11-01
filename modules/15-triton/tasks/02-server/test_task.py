import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pytest
from course_tasks import load_solution

try:
    import onnxruntime as ort
except ModuleNotFoundError as exc:
    if exc.name != "onnxruntime":
        raise
    ort = None

s = load_solution(__file__)


def test_batch_axis_is_in_shape_not_in_feature_dimensions():
    result = s.inference_request([{"b": 2, "a": 1}, {"a": 3, "b": 4}], ["a", "b"])
    assert result == {
        "inputs": [
            {
                "name": "features",
                "datatype": "FP32",
                "shape": [2, 2],
                "data": [1.0, 2.0, 3.0, 4.0],
            }
        ]
    }


def test_empty_and_oversized_batch_are_rejected():
    with pytest.raises(ValueError):
        s.inference_request([], ["a"])
    with pytest.raises(ValueError):
        s.inference_request([{"a": 1}] * 33, ["a"])


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1",
    reason="Дополнительный Linux Triton runtime",
)
def test_live_server_and_model_are_both_ready():
    assert ort is not None, (
        "Install labs/triton/requirements.txt before enabling this probe"
    )
    base = os.getenv("TRITON_URL", "http://127.0.0.1:8000")
    for path in ["/v2/health/ready", "/v2/models/housing/ready"]:
        with urlopen(base + path, timeout=5) as response:
            assert response.status == 200

    model_path = Path(
        os.getenv(
            "TRITON_ONNX_PATH", "work/triton/model_repository/housing/1/model.onnx"
        )
    )
    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    features = np.array([[8.3, 41, 6.9, 1.0, 322, 2.5, 37.8, -122.2]], dtype=np.float32)
    expected = session.run(None, {"features": features})
    body = s.inference_request(
        [dict(zip(["a", "b", "c", "d", "e", "f", "g", "h"], features[0].tolist()))],
        ["a", "b", "c", "d", "e", "f", "g", "h"],
    )
    request = Request(
        base + "/v2/models/housing/infer",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=10) as response:
        observed = json.load(response)["outputs"]
    assert {row["name"] for row in observed} == {
        out.name for out in session.get_outputs()
    }
    by_name = {row["name"]: row for row in observed}
    for output, values in zip(session.get_outputs(), expected):
        actual = by_name[output.name]
        result = np.asarray(actual["data"]).reshape(actual["shape"])
        assert np.isfinite(result).all()
        np.testing.assert_allclose(result, values, rtol=1e-4, atol=1e-5)


@pytest.mark.parametrize("count,max_batch", [(1, 32), (32, 32), (3, 3), (33, 40)])
def test_batch_limits_and_row_major_feature_order(count, max_batch):
    rows = [{"b": index + 0.5, "a": index} for index in range(count)]
    result = s.inference_request(rows, ["a", "b"], max_batch=max_batch)
    assert result == {
        "inputs": [
            {
                "name": "features",
                "datatype": "FP32",
                "shape": [count, 2],
                "data": [
                    value
                    for index in range(count)
                    for value in (float(index), index + 0.5)
                ],
            }
        ]
    }


def test_custom_batch_limit_and_invalid_features_are_not_hidden():
    with pytest.raises(ValueError):
        s.inference_request([{"a": 1}] * 4, ["a"], max_batch=3)
    with pytest.raises(ValueError):
        s.inference_request([{"a": 1}, {"a": True}], ["a"])

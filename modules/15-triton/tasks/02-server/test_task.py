from types import SimpleNamespace
from unittest.mock import Mock

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

try:
    import onnx
except ModuleNotFoundError as exc:
    if exc.name != "onnx":
        raise
    onnx = None

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


def test_cli_client_boundary_normalizes_url(monkeypatch):
    constructor = Mock()
    monkeypatch.setattr(
        s, "httpclient", SimpleNamespace(InferenceServerClient=constructor)
    )
    s.create_client("http://127.0.0.1:8000", timeout=3)
    constructor.assert_called_once_with(
        url="127.0.0.1:8000",
        ssl=False,
        connection_timeout=3,
        network_timeout=3,
    )


def test_missing_http_sdk_has_install_command(monkeypatch):
    monkeypatch.setattr(s, "httpclient", None)
    with pytest.raises(RuntimeError, match="labs/triton/client-requirements.txt"):
        s.infer(None, [], ["a"])


@pytest.mark.sdk
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_SDK") != "1",
    reason="Real Triton HTTP types and ONNX Runtime opt-in",
)
def test_student_infer_uses_real_sdk_tensors_and_matches_synthetic_onnx():
    assert s.httpclient is not None, (
        "Install labs/triton/client-requirements.txt in a compatible client environment"
    )
    assert ort is not None, "Install labs/triton/requirements.txt"
    assert onnx is not None, "Install labs/triton/requirements.txt"
    helper, TensorProto, numpy_helper = onnx.helper, onnx.TensorProto, onnx.numpy_helper
    graph = helper.make_graph(
        [helper.make_node("MatMul", ["features", "weights"], ["variable"])],
        "tiny-tabular-housing",
        [helper.make_tensor_value_info("features", TensorProto.FLOAT, [None, 2])],
        [helper.make_tensor_value_info("variable", TensorProto.FLOAT, [None, 1])],
        [
            numpy_helper.from_array(
                np.array([[2.0], [3.0]], dtype=np.float32), name="weights"
            )
        ],
    )
    model = helper.make_model(
        graph, opset_imports=[helper.make_opsetid("", 17)], ir_version=9
    )
    onnx.checker.check_model(model)
    session = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"]
    )
    expected = session.run(
        None, {"features": np.array([[1, 2], [3, 4]], dtype=np.float32)}
    )[0]

    class ClientBoundary:
        """Transport double only; real SDK tensors and real ORT are used, no server is emulated."""

        calls = 0

        def infer(self, model_name, inputs, outputs, **kwargs):
            self.calls += 1
            assert model_name == "housing"
            assert len(inputs) == len(outputs) == 1
            tensor, output = inputs[0], outputs[0]
            assert isinstance(tensor, s.httpclient.InferInput)
            assert isinstance(output, s.httpclient.InferRequestedOutput)
            assert tensor.name() == "features" and tensor.datatype() == "FP32"
            assert tensor.shape() == [2, 2] and output.name() == "variable"
            matrix = np.frombuffer(tensor._get_binary_data(), dtype=np.float32).reshape(
                tensor.shape()
            )
            values = session.run(None, {"features": matrix})[0]
            return s.httpclient.InferResult.from_response_body(
                json.dumps(
                    {
                        "outputs": [
                            {
                                "name": "variable",
                                "datatype": "FP32",
                                "shape": list(values.shape),
                                "data": values.reshape(-1).tolist(),
                            }
                        ]
                    }
                ).encode()
            )

    client = ClientBoundary()
    actual = s.infer(client, [{"b": 2, "a": 1}, {"a": 3, "b": 4}], ["a", "b"])
    assert client.calls == 1 and set(actual) == {"variable"}
    assert actual["variable"].dtype == np.float32
    np.testing.assert_allclose(actual["variable"], expected, rtol=1e-4, atol=1e-5)


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1",
    reason="Existing compatible Triton server opt-in",
)
def test_live_student_sdk_infer_matches_exported_onnx():
    assert s.httpclient is not None, "Install labs/triton/client-requirements.txt"
    assert ort is not None, "Install labs/triton/requirements.txt"
    path = Path(
        os.getenv(
            "TRITON_ONNX_PATH", "work/triton/model_repository/housing/1/model.onnx"
        )
    )
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    matrix = np.array([[8.3, 41, 6.9, 1, 322, 2.5, 37.8, -122.2]], dtype=np.float32)
    order = list("abcdefgh")
    names = [output.name for output in session.get_outputs()]
    with s.create_client(os.getenv("TRITON_URL", "http://127.0.0.1:8000")) as client:
        assert client.is_server_ready() and client.is_model_ready("housing")
        actual = s.infer(
            client, [dict(zip(order, matrix[0].tolist()))], order, output_names=names
        )
    assert set(actual) == set(names)
    for name, expected in zip(names, session.run(None, {"features": matrix})):
        assert np.isfinite(actual[name]).all()
        assert actual[name].shape == expected.shape
        np.testing.assert_allclose(actual[name], expected, rtol=1e-4, atol=1e-5)

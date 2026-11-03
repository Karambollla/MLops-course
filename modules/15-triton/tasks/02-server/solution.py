"""Учебный tabular ONNX клиент Triton; импорт не обращается к серверу."""

# ruff: noqa: F401
# SDK/численные импорты подготовлены для student-реализации.

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from course_tasks import load_task
from housing.features import FEATURES

try:
    import tritonclient.http as httpclient
except ModuleNotFoundError as exc:
    if exc.name != "tritonclient":
        raise
    httpclient = None


def inference_request(
    rows: list[dict], feature_order: list[str], max_batch: int = 32
) -> dict:
    raise NotImplementedError(
        "Используй feature_matrix из 15-triton/01-onnx и собери HTTP V2 request"
    )


def infer(
    client,
    rows: list[dict],
    feature_order: list[str],
    model_name="housing",
    output_names=("variable",),
    max_batch=32,
) -> dict[str, np.ndarray]:
    """Отправь FP32 tensor SDK-клиентом; верни именованные numpy outputs."""
    if httpclient is None:
        raise RuntimeError(
            "Install SDK in a separate client environment: "
            "python -m pip install -r labs/triton/client-requirements.txt"
        )
    # TODO(student): feature_matrix -> InferInput/set_data_from_numpy ->
    # InferRequestedOutput -> client.infer -> result.as_numpy по каждому имени.
    raise NotImplementedError("infer: реализуй вызов tritonclient.http")


def create_client(url, timeout=10):
    """CLI принимает http(s) URL; SDK ожидает host:port без схемы."""
    if httpclient is None:
        raise RuntimeError(
            "Install SDK: python -m pip install -r labs/triton/client-requirements.txt"
        )
    parsed = urlparse(url if "://" in url else "http://" + url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("TRITON_URL must be http(s)://host:port without a path")
    return httpclient.InferenceServerClient(
        url=parsed.netloc,
        ssl=parsed.scheme == "https",
        connection_timeout=timeout,
        network_timeout=timeout,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rows", required=True, type=Path, help="JSON list of housing rows"
    )
    parser.add_argument(
        "--url", default=os.getenv("TRITON_URL", "http://127.0.0.1:8000")
    )
    parser.add_argument("--model", default="housing")
    parser.add_argument("--features", nargs="+", default=list(FEATURES))
    parser.add_argument("--outputs", nargs="+", default=["variable"])
    args = parser.parse_args()
    rows = json.loads(args.rows.read_text(encoding="utf-8"))
    with create_client(args.url) as client:
        outputs = infer(
            client,
            rows,
            args.features,
            model_name=args.model,
            output_names=args.outputs,
        )
    print(
        json.dumps(
            {
                "model": args.model,
                "outputs": [
                    {
                        "name": name,
                        "shape": list(values.shape),
                        "datatype": str(values.dtype),
                        "data": values.tolist(),
                    }
                    for name, values in outputs.items()
                ],
            },
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()

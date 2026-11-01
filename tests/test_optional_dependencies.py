"""Optional SDKs do not prevent collecting the course's base tests."""

import sys
from pathlib import Path

import pytest
from course_tasks import load_task


def test_clearml_cli_explains_how_to_install_missing_sdk(monkeypatch, tmp_path):
    solution = load_task("06-clearml/01-offline")
    monkeypatch.setattr(solution, "Task", None, raising=False)
    monkeypatch.setitem(sys.modules, "clearml", None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "solution.py",
            "--data",
            str(tmp_path / "data.csv"),
            "--output",
            str(tmp_path),
        ],
    )
    with pytest.raises(RuntimeError, match="labs/clearml/requirements.txt"):
        solution.main()


@pytest.mark.parametrize(
    "task_id,function,args,sdk_names,requirements",
    [
        (
            "04-mlflow/01-experiments",
            "track_experiments",
            (Path("data.csv"), Path("output"), "http://127.0.0.1:5001"),
            ("mlflow",),
            "labs/mlflow/requirements.txt",
        ),
        (
            "04-mlflow/02-registry",
            "register_model",
            (None, None, "run-1", "housing", "http://127.0.0.1:5001"),
            ("mlflow",),
            "labs/mlflow/requirements.txt",
        ),
        (
            "13-qdrant/01-plumbing",
            "index_documents",
            ("http://127.0.0.1:6333", Path("corpus.json")),
            ("QdrantClient", "models"),
            "labs/qdrant/requirements.txt",
        ),
        (
            "15-triton/01-onnx",
            "export_bundle",
            (Path("model.joblib"), Path("model.onnx")),
            ("onnx", "ort", "convert_sklearn", "FloatTensorType"),
            "labs/triton/requirements.txt",
        ),
    ],
)
def test_functions_explain_missing_sdk(
    monkeypatch, task_id, function, args, sdk_names, requirements
):
    solution = load_task(task_id)
    for name in sdk_names:
        monkeypatch.setattr(solution, name, None, raising=False)
    with pytest.raises(RuntimeError, match=requirements):
        getattr(solution, function)(*args)

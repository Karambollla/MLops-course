"""Offline проверки поведения; исходная заготовка должна быть RED."""

import os

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    import mlflow
    import mlflow.sklearn
    from mlflow.tracking import MlflowClient
except ModuleNotFoundError as exc:
    if exc.name != "mlflow":
        raise
    mlflow = MlflowClient = None

from types import SimpleNamespace

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


class Client:
    def get_model_version_by_alias(self, name, alias):
        assert (name, alias) == ("housing", "champion")
        return SimpleNamespace(version="7", run_id="run-1")


class Model:
    def __init__(self, values):
        self.values = values

    def predict(self, batch):
        return self.values


def test_alias_is_resolved():
    assert s.resolve_release(Client(), "housing", "champion", "run-1") == {
        "model_name": "housing",
        "alias": "champion",
        "version": "7",
        "run_id": "run-1",
        "model_uri": "models:/housing/7",
    }
    with pytest.raises(ValueError):
        s.resolve_release(Client(), "housing", "champion", "other")


def test_prediction_parity():
    assert (
        s.assert_parity(Model([1.0, 2.0]), Model([1.0 + 1e-9, 2.0]), [{}, {}]) is None
    )
    for values in [[1.0], [1.0, 3.0], [1.0, float("nan")]]:
        with pytest.raises(ValueError):
            s.assert_parity(Model([1.0, 2.0]), Model(values), [{}, {}])


@pytest.mark.parametrize("version", ["1", "12", 3])
def test_release_pins_positive_version_and_exact_source(version):
    client = SimpleNamespace(
        get_model_version_by_alias=lambda name, alias: SimpleNamespace(
            version=version, run_id="source-99"
        )
    )
    release = s.resolve_release(client, "housing-v2", "candidate", "source-99")
    assert release == {
        "model_name": "housing-v2",
        "alias": "candidate",
        "version": str(version),
        "run_id": "source-99",
        "model_uri": f"models:/housing-v2/{version}",
    }


@pytest.mark.parametrize("version", ["0", "-1", "1.5", "latest", "", 0, -2])
def test_release_rejects_nonpositive_or_noninteger_versions(version):
    client = SimpleNamespace(
        get_model_version_by_alias=lambda name, alias: SimpleNamespace(
            version=version, run_id="source"
        )
    )
    with pytest.raises(ValueError):
        s.resolve_release(client, "housing", "champion", "source")


@pytest.mark.parametrize(
    "original,registered",
    [
        ([1.0, 2.0], [[1.0], [2.0]]),
        ([float("inf"), 2.0], [float("inf"), 2.0]),
        ([float("nan"), 2.0], [1.0, 2.0]),
        ([1.0, 2.0], [1.0, -float("inf")]),
        ([1.0, 2.0], [1.0001, 2.0]),
    ],
)
def test_parity_rejects_shape_nonfinite_and_outside_tolerance(original, registered):
    with pytest.raises(ValueError):
        s.assert_parity(Model(original), Model(registered), [{}, {}])


def test_parity_uses_documented_relative_and_absolute_tolerances():
    assert (
        s.assert_parity(Model([0.0, 1000.0]), Model([5e-9, 1000.0005]), [{}, {}])
        is None
    )


@pytest.mark.sdk
def test_sdk_registers_pipeline_signature_example_and_pinned_release(
    tmp_path, monkeypatch
):
    if os.getenv("MLOPS_RUN_SDK") != "1":
        pytest.skip("Set MLOPS_RUN_SDK=1 to run the pinned local MLflow SDK test")
    if mlflow is None:
        pytest.fail(
            "Install MLflow SDK: python -m pip install -r labs/mlflow/requirements.txt"
        )
    assert mlflow.__version__ == "3.1.1", (
        "Use labs/mlflow/requirements.txt (MLflow 3.1.1)"
    )
    previous_tracking, previous_registry = (
        mlflow.get_tracking_uri(),
        mlflow.get_registry_uri(),
    )
    previous_experiment = mlflow.tracking.fluent._active_experiment_id
    if mlflow.active_run() is not None:
        pytest.fail(
            "SDK tests require no active MLflow run; refusing to close a caller's run"
        )
    uri = f"sqlite:///{tmp_path / 'registry.db'}"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MLFLOW_ENABLE_ASYNC_LOGGING", "false")
    try:
        mlflow.set_tracking_uri(uri)
        mlflow.set_registry_uri(uri)
        client = MlflowClient(tracking_uri=uri, registry_uri=uri)
        experiment = client.create_experiment(
            "registry-test", artifact_location=(tmp_path / "artifacts").as_uri()
        )
        frame = pd.DataFrame(
            {"x": np.linspace(-2, 2, 30), "y": np.linspace(3, 7, 30) ** 2}
        )
        pipeline = Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=0.17))])
        pipeline.fit(frame, 1.7 * frame.x + 0.2 * frame.y)
        example = frame.iloc[:4]
        with mlflow.start_run(experiment_id=experiment) as run:
            run_id = run.info.run_id
        release = s.register_model(pipeline, example, run_id, "housing-test", uri)
        # Fresh client reads actual persisted registry links and aliases.
        client = MlflowClient(tracking_uri=uri, registry_uri=uri)
        assert release["model_name"] == "housing-test"
        assert release["run_id"] == run_id
        assert int(release["version"]) > 0
        assert release["model_uri"] == f"models:/housing-test/{release['version']}"
        version = client.get_model_version("housing-test", release["version"])
        assert version.run_id == run_id
        for alias in ("candidate", "champion"):
            resolved = client.get_model_version_by_alias("housing-test", alias)
            assert resolved.version == release["version"] and resolved.run_id == run_id
        info = mlflow.models.get_model_info(release["model_uri"])
        assert info.signature is not None and info.signature.inputs is not None
        assert info.saved_input_example_info
        loaded = mlflow.sklearn.load_model(release["model_uri"])
        assert isinstance(loaded, Pipeline)
        original_predictions, registered_predictions = (
            pipeline.predict(frame),
            loaded.predict(frame),
        )
        assert original_predictions.shape == registered_predictions.shape
        assert np.isfinite(registered_predictions).all()
        np.testing.assert_allclose(
            original_predictions, registered_predictions, rtol=1e-6, atol=1e-8
        )
        s.assert_parity(pipeline, loaded, frame)
    finally:
        if mlflow.active_run() is not None:
            mlflow.end_run()
        mlflow.set_tracking_uri(previous_tracking)
        mlflow.set_registry_uri(previous_registry)
        mlflow.tracking.fluent._active_experiment_id = previous_experiment

"""Opt-in server resources, isolated from the learner's existing experiments."""

import os
from types import SimpleNamespace
from uuid import uuid4

import pytest

try:
    import mlflow
    import mlflow.sklearn
    from mlflow.exceptions import MlflowException
    from mlflow.tracking import MlflowClient
except ModuleNotFoundError as exc:
    if exc.name != "mlflow":
        raise
    mlflow = MlflowClient = MlflowException = None


@pytest.fixture
def mlflow_server(monkeypatch):
    if not (
        os.getenv("MLOPS_RUN_INTEGRATION") == "1"
        and os.getenv("MLOPS_RUN_WRITES") == "1"
    ):
        pytest.skip("Server writes require MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1")
    if mlflow is None:
        pytest.fail("Install labs/mlflow/requirements.txt before enabling server tests")
    assert mlflow.__version__ == "3.1.1"
    if mlflow.active_run() is not None:
        pytest.fail("Refusing to close a caller's active MLflow run")
    uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001")
    assert uri.startswith(("http://", "https://")), "Use the running HTTP server"
    previous = mlflow.get_tracking_uri(), mlflow.get_registry_uri()
    previous_experiment = mlflow.tracking.fluent._active_experiment_id
    name = "course-integration-" + uuid4().hex
    client = MlflowClient(tracking_uri=uri, registry_uri=uri)
    experiment_id = None
    try:
        mlflow.set_tracking_uri(uri)
        mlflow.set_registry_uri(uri)
        monkeypatch.setenv("MLFLOW_ENABLE_ASYNC_LOGGING", "false")
        # Server default artifact location exercises the HTTP artifact proxy.
        experiment_id = client.create_experiment(name)
        yield SimpleNamespace(
            sdk=mlflow,
            client=client,
            uri=uri,
            name=name,
            experiment_id=experiment_id,
            model_name=name + "-model",
        )
    finally:
        try:
            if mlflow.active_run() is not None:
                mlflow.end_run(status="FAILED")
            # Only this fixture's unique model and experiment may be removed.
            if experiment_id is not None:
                try:
                    client.delete_registered_model(name + "-model")
                except MlflowException as error:
                    if error.error_code != "RESOURCE_DOES_NOT_EXIST":
                        raise
                finally:
                    for run in client.search_runs([experiment_id]):
                        client.delete_run(run.info.run_id)
                    client.delete_experiment(experiment_id)
        finally:
            mlflow.set_tracking_uri(previous[0])
            mlflow.set_registry_uri(previous[1])
            mlflow.tracking.fluent._active_experiment_id = previous_experiment

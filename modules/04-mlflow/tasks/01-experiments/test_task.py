"""Offline проверки поведения; исходная заготовка должна быть RED."""

# Exercise the student's tracking function; only the SDK boundary is replaced.
# Training stays real, including any prerequisite exercises still to implement.
import hashlib
import io
import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import joblib
import numpy as np
import pandas as pd
from housing.features import FEATURES, TARGET
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

try:
    import mlflow
    from mlflow.tracking import MlflowClient
except ModuleNotFoundError as exc:
    if exc.name != "mlflow":
        raise
    mlflow = MlflowClient = None


import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def runs():
    return [
        {
            "run_id": str(i),
            "status": "FINISHED",
            "parameters": {"alpha": i},
            "data_sha256": "a" * 64,
            "split": {"train": [0], "validation": [1], "test": [2]},
            "validation_mae": m,
            "validation_rmse": m + 0.1,
            "test_mae": 10 - i,
        }
        for i, m in enumerate([0.8, 0.5, 0.6])
    ]


def test_validation_selects_not_test():
    r = runs()
    assert s.select_candidate(r) == "1"
    r[0]["test_mae"] = 0.0
    assert s.select_candidate(r) == "1"


@pytest.mark.parametrize(
    "mutation", ["hash", "split", "status", "nan", "duplicate", "count"]
)
def test_incomparable_experiments(mutation):
    r = runs()
    if mutation == "hash":
        r[1]["data_sha256"] = "b" * 64
    if mutation == "split":
        r[1]["split"]["test"] = [3]
    if mutation == "status":
        r[1]["status"] = "FAILED"
    if mutation == "nan":
        r[1]["validation_mae"] = float("nan")
    if mutation == "duplicate":
        r[1]["parameters"] = r[0]["parameters"]
    if mutation == "count":
        r = r[:2]
    with pytest.raises(ValueError):
        s.select_candidate(r)


@pytest.mark.parametrize(
    "order", [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
)
def test_tie_uses_run_id_independent_of_order(order):
    records = runs()
    for record, run_id in zip(records, ["z-run", "a-run", "m-run"]):
        record.update(run_id=run_id, validation_mae=0.0)
    assert s.select_candidate([records[i] for i in order]) == "a-run"


@pytest.mark.parametrize("metric", ["validation_mae", "validation_rmse"])
@pytest.mark.parametrize("value", [-0.01, float("inf"), -float("inf"), float("nan")])
def test_invalid_validation_measurements(metric, value):
    records = runs()
    records[2][metric] = value
    with pytest.raises(ValueError):
        s.select_candidate(records)


@pytest.mark.parametrize("part", ["train", "validation", "test"])
def test_every_split_partition_must_match(part):
    records = runs()
    records[0]["split"][part] = [99]
    with pytest.raises(ValueError):
        s.select_candidate(records)


@pytest.mark.parametrize("status", ["RUNNING", "KILLED", "SCHEDULED"])
def test_every_run_must_be_finished(status):
    records = runs()
    records[2]["status"] = status
    with pytest.raises(ValueError):
        s.select_candidate(records)


def test_parameters_comparison_uses_values_not_mapping_order():
    records = runs()
    records[0]["parameters"] = {"alpha": 1, "seed": 42}
    records[1]["parameters"] = {"seed": 42, "alpha": 1}
    with pytest.raises(ValueError):
        s.select_candidate(records)


def small_data(tmp_path, seed):
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame(rng.uniform(1, 3, (100, len(FEATURES))), columns=FEATURES)
    frame[TARGET] = (
        1.7 * frame.MedInc + frame.Latitude + rng.normal(0, 0.03, len(frame))
    )
    path = tmp_path / "housing.csv"
    frame.to_csv(path, index=False)
    return path


def json_contains(container, expected):
    """Accept nested or JSON-encoded SDK parameter values without prescribing layout."""
    if container == expected:
        return True
    if isinstance(container, str):
        try:
            decoded = json.loads(container)
        except (ValueError, TypeError):
            return False
        return decoded != container and json_contains(decoded, expected)
    if isinstance(container, dict):
        return any(json_contains(value, expected) for value in container.values())
    if isinstance(container, list):
        return any(json_contains(value, expected) for value in container)
    return False


def assert_training_records(data, output, records, persisted):
    assert len(records) == len(persisted) == 3
    assert len({record["run_id"] for record in records}) == 3
    assert (
        len({json.dumps(record["parameters"], sort_keys=True) for record in records})
        == 3
    )
    assert {record["parameters"]["alpha"] for record in records} == {0.1, 1.0, 10.0}
    comparison = json.loads((output / "comparison.json").read_text())
    for record in records:
        logged = persisted[record["run_id"]]
        assert logged["status"] == record["status"] == "FINISHED"
        files = logged["files"]
        # log_artifacts may place a bundle beneath an artifact subdirectory.
        by_name = {Path(name).name: content for name, content in files.items()}
        assert {
            "model.joblib",
            "metrics.json",
            "manifest.json",
            "split.json",
        } <= by_name.keys()
        measured = json.loads(by_name["metrics.json"])["candidate"]
        manifest = json.loads(by_name["manifest.json"])
        split = json.loads(by_name["split.json"])
        assert manifest["split"] == record["split"] == split
        assert (
            manifest["data_sha256"]
            == record["data_sha256"]
            == hashlib.sha256(data.read_bytes()).hexdigest()
        )
        assert manifest["parameters"] == record["parameters"]
        assert manifest["versions"]
        bundle = joblib.load(io.BytesIO(by_name["model.joblib"]))
        assert isinstance(bundle["pipeline"], Pipeline)
        estimator = bundle["pipeline"].steps[-1][1]
        assert isinstance(estimator, Ridge)
        assert estimator.alpha == pytest.approx(record["parameters"]["alpha"])
        assert manifest["seed"] == 42
        frame = pd.read_csv(data)
        for part in ("validation", "test"):
            rows = frame.iloc[split[part]]
            predictions = bundle["pipeline"].predict(rows[FEATURES])
            errors = predictions - rows[TARGET].to_numpy()
            assert np.isfinite(predictions).all()
            assert measured[part]["mae"] == pytest.approx(np.mean(np.abs(errors)))
            assert measured[part]["rmse"] == pytest.approx(np.sqrt(np.mean(errors**2)))
            for metric in ("mae", "rmse"):
                assert logged["metrics"][f"{part}_{metric}"] == pytest.approx(
                    measured[part][metric]
                )
        for metric in ("mae", "rmse"):
            value = measured["validation"][metric]
            assert np.isfinite(value) and value >= 0
            assert record[f"validation_{metric}"] == pytest.approx(value)
            assert any(v == pytest.approx(value) for v in logged["metrics"].values())
        # SDK params may be flattened, nested, or JSON serialized.
        assert json_contains(logged["params"], record["data_sha256"])
        assert json_contains(logged["params"], manifest["seed"])
        for key, value in manifest["parameters"].items():
            assert json_contains(logged["params"], value)
        for value in manifest["versions"].values():
            assert json_contains(logged["params"], value)
        assert json_contains(comparison, record["run_id"])
        assert json_contains(comparison, record["validation_mae"])
        assert json_contains(comparison, record["validation_rmse"])
    assert all(record["split"] == records[0]["split"] for record in records)


@pytest.mark.parametrize("seed", [13, 89])
def test_tracking_logs_measured_training_artifacts(tmp_path, monkeypatch, seed):
    persisted = {}
    current = []
    uris, experiments = [], []

    @contextmanager
    def start_run(**kwargs):
        run_id = f"test-run-{len(persisted)}"
        record = {"params": {}, "metrics": {}, "files": {}, "status": "RUNNING"}
        persisted[run_id] = record
        current.append(record)
        try:
            yield SimpleNamespace(info=SimpleNamespace(run_id=run_id))
            record["status"] = "FINISHED"
        finally:
            current.pop()

    def log_artifacts(local_dir, artifact_path=None, **kwargs):
        for path in Path(local_dir).rglob("*"):
            if path.is_file():
                name = str(Path(artifact_path or "") / path.relative_to(local_dir))
                current[-1]["files"][name] = path.read_bytes()

    def set_experiment(experiment_name):
        experiments.append(experiment_name)
        return SimpleNamespace(experiment_id="test-experiment", name=experiment_name)

    sdk = SimpleNamespace(
        set_tracking_uri=uris.append,
        set_experiment=set_experiment,
        start_run=start_run,
        log_params=lambda params: current[-1]["params"].update(params),
        log_metrics=lambda metrics, **kw: current[-1]["metrics"].update(metrics),
        log_artifacts=log_artifacts,
    )
    monkeypatch.setattr(s, "mlflow", sdk)
    data = small_data(tmp_path, seed)
    output = tmp_path / "runs"
    records = s.track_experiments(data, output, "test://tracking")
    assert "test://tracking" in uris and "housing-course" in experiments
    assert_training_records(data, output, records, persisted)


@pytest.mark.sdk
def test_sdk_tracking_persists_three_real_runs(tmp_path, monkeypatch):
    if s.os.getenv("MLOPS_RUN_SDK") != "1":
        pytest.skip("Set MLOPS_RUN_SDK=1 to run the pinned local MLflow SDK test")
    if mlflow is None:
        pytest.fail(
            "Install MLflow SDK: python -m pip install -r labs/mlflow/requirements.txt"
        )
    assert mlflow.__version__ == "3.1.1", (
        "Use labs/mlflow/requirements.txt (MLflow 3.1.1)"
    )
    monkeypatch.setenv("MLFLOW_ENABLE_ASYNC_LOGGING", "false")
    previous_tracking, previous_registry = (
        mlflow.get_tracking_uri(),
        mlflow.get_registry_uri(),
    )
    previous_experiment = mlflow.tracking.fluent._active_experiment_id
    if mlflow.active_run() is not None:
        pytest.fail(
            "SDK tests require no active MLflow run; refusing to close a caller's run"
        )
    uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    try:
        mlflow.set_tracking_uri(uri)
        mlflow.set_registry_uri(uri)
        client = MlflowClient(tracking_uri=uri, registry_uri=uri)
        client.create_experiment(
            "housing-course", artifact_location=(tmp_path / "artifacts").as_uri()
        )
        data = small_data(tmp_path, 23)
        output = tmp_path / "runs"
        records = s.track_experiments(data, output, uri)
        # Re-create the client to inspect persisted metadata rather than fake call history.
        client = MlflowClient(tracking_uri=uri, registry_uri=uri)
        experiment = client.get_experiment_by_name("housing-course")
        stored = client.search_runs([experiment.experiment_id])
        persisted = {}
        for run in stored:
            files = {}
            todo = [""]
            while todo:
                for item in client.list_artifacts(run.info.run_id, todo.pop()):
                    if item.is_dir:
                        todo.append(item.path)
                    else:
                        local = client.download_artifacts(
                            run.info.run_id, item.path, str(tmp_path)
                        )
                        files[item.path] = Path(local).read_bytes()
            persisted[run.info.run_id] = {
                "status": run.info.status,
                "params": run.data.params,
                "metrics": run.data.metrics,
                "files": files,
            }
        assert_training_records(data, output, records, persisted)
    finally:
        if mlflow.active_run() is not None:
            mlflow.end_run()
        mlflow.set_tracking_uri(previous_tracking)
        mlflow.set_registry_uri(previous_registry)
        mlflow.tracking.fluent._active_experiment_id = previous_experiment


@pytest.mark.parametrize("count", [0, 1, 4])
def test_requires_exactly_three_runs(count):
    records = runs()
    if count == 4:
        records.append(dict(records[0], run_id="fourth", parameters={"alpha": 99}))
    else:
        records = records[:count]
    with pytest.raises(ValueError):
        s.select_candidate(records)


@pytest.mark.integration
@pytest.mark.writes
def test_server_records_real_training_and_downloadable_artifacts(
    tmp_path, mlflow_server
):
    server = mlflow_server
    data, output = small_data(tmp_path, 67), tmp_path / "server-runs"
    records = s.track_experiments(data, output, server.uri, experiment_name=server.name)
    persisted = {}
    for run in server.client.search_runs([server.experiment_id]):
        files, pending_paths = {}, [""]
        while pending_paths:
            for item in server.client.list_artifacts(
                run.info.run_id, pending_paths.pop()
            ):
                if item.is_dir:
                    pending_paths.append(item.path)
                else:
                    path = server.client.download_artifacts(
                        run.info.run_id, item.path, str(tmp_path)
                    )
                    files[item.path] = Path(path).read_bytes()
        persisted[run.info.run_id] = {
            "status": run.info.status,
            "params": run.data.params,
            "metrics": run.data.metrics,
            "files": files,
        }
    assert_training_records(data, output, records, persisted)

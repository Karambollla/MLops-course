"""These checks build/execute the learner's DAG using the real Airflow SDK."""

import json

import pytest
from course_tasks import load_task

pytestmark = pytest.mark.sdk


def test_real_dag_structure_without_training_at_parse_time(
    build, monkeypatch, tmp_path, dag_type
):
    s = load_task("05-airflow/01-pipeline")
    original = s.load_task

    def forbidden(*args, **kwargs):
        pytest.fail("DAG parsing must not train, read CSV or publish")

    def only_stage_one(task_id, **kwargs):
        assert task_id not in {
            "05-airflow/02-gate-retry",
            "05-airflow/03-failure-intervals",
        }
        return original(task_id, **kwargs)

    monkeypatch.setattr(s, "prepare_training", forbidden)
    monkeypatch.setattr(s, "run_training", forbidden)
    monkeypatch.setattr(s, "load_task", only_stage_one)
    dag = build(1)
    assert isinstance(dag, dag_type)
    assert dag.dag_id == "housing_pipeline"
    assert set(dag.task_ids) == {"validate_data", "train_evaluate"}
    assert dag.get_task("validate_data").downstream_task_ids == {"train_evaluate"}
    assert dag.catchup is False and dag.max_active_runs == 1
    assert dag.schedule is None
    assert list(tmp_path.iterdir()) == []


def test_training_executes_and_xcom_contains_only_model_reference(execute_dag):
    result, folder = execute_dag(1)
    assert result["state"] == "success", result
    assert all(v["state"] == "success" for v in result["tasks"].values())
    metadata = result["xcom"]["train_evaluate"]
    assert set(metadata) == {"path", "run_key", "model_version"}
    assert len(json.dumps(metadata)) < 4096
    output = folder / "runs" / metadata["run_key"]
    assert metadata["path"] == str(output)
    assert isinstance(metadata["model_version"], str) and metadata["model_version"]
    for name in ("model.joblib", "metrics.json", "manifest.json", "split.json"):
        assert (output / name).stat().st_size > 0
    assert json.loads((output / "manifest.json").read_text())["seed"] == 17


def test_missing_csv_fails_validate_and_blocks_training(execute_dag):
    result, folder = execute_dag(1, data_path="/nonexistent-course-input.csv")
    assert result["state"] == "failed"
    assert result["tasks"]["validate_data"]["state"] == "failed"
    assert result["tasks"]["train_evaluate"]["state"] == "upstream_failed"
    assert not (folder / "runs").exists()

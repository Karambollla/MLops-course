"""Real SDK graph and task execution; scheduler retry is checked separately."""

import json
from datetime import timedelta

import pytest

pytestmark = pytest.mark.sdk


def test_gate_dependencies_and_airflow_retry_settings(build):
    dag = build(2)
    assert set(dag.task_ids) == {"validate_data", "train_evaluate", "gate", "publish"}
    assert dag.get_task("train_evaluate").downstream_task_ids == {"gate"}
    assert dag.get_task("gate").downstream_task_ids == {"publish"}
    assert dag.get_task("gate").retries == 0
    assert dag.get_task("publish").retries == 1
    assert dag.get_task("publish").retry_delay == timedelta(seconds=1)
    assert dag.get_task("publish").trigger_rule == "all_success"


def test_successful_release_matches_training_metadata(execute_dag):
    result, folder = execute_dag(2)
    assert result["state"] == "success", result
    metadata = result["xcom"]["train_evaluate"]
    releases = list((folder / "releases").glob("*.json"))
    assert len(releases) == 1
    release = json.loads(releases[0].read_text())
    assert release == result["xcom"]["publish"]
    assert release["run_key"] == metadata["run_key"]
    assert release["model_version"] == metadata["model_version"]
    assert release["model_path"] == metadata["path"] + "/model.joblib"


def test_rejection_is_a_failed_gate_and_has_no_release(execute_dag):
    result, folder = execute_dag(2, gate_ratio=0.0)
    assert result["state"] == "failed", result
    assert result["tasks"]["train_evaluate"]["state"] == "success"
    assert result["tasks"]["gate"]["state"] == "failed"
    assert result["tasks"]["gate"]["attempts"] == 1
    assert result["tasks"]["publish"]["state"] == "upstream_failed"
    assert not list((folder / "releases").glob("*.json"))

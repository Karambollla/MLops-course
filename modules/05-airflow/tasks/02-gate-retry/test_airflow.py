"""Observe completed learner DAG runs; never trigger, clear or change tasks."""

import json
import os
import subprocess
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("MLOPS_RUN_INTEGRATION") != "1",
        reason="Existing completed Airflow run required",
    ),
]


def test_real_task_states_and_publish_attempts():
    run_id = os.environ["AIRFLOW_ACCEPTANCE_RUN_ID"]
    expected = os.getenv("AIRFLOW_EXPECT_GATE", "pass")
    assert expected in {"pass", "reject"}
    script = """
import json, sys
from airflow.models.taskinstance import TaskInstance
from airflow.utils.session import create_session
with create_session() as session:
    rows = session.query(TaskInstance).filter(TaskInstance.dag_id == "housing_pipeline", TaskInstance.run_id == sys.argv[1]).all()
    print(json.dumps({row.task_id: {"state": row.state, "attempts": row.try_number} for row in rows}))
"""
    root = Path(__file__).resolve().parents[4]
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(root / "labs/airflow/compose.yaml"),
            "exec",
            "-T",
            "airflow",
            "python",
            "-c",
            script,
            run_id,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    states = json.loads(result.stdout.strip().splitlines()[-1])
    assert {"validate_data", "train_evaluate", "gate", "publish"} <= set(states)
    assert (
        states["validate_data"]["state"]
        == states["train_evaluate"]["state"]
        == "success"
    )
    if expected == "pass":
        assert states["gate"]["state"] == states["publish"]["state"] == "success"
        assert states["publish"]["attempts"] >= int(
            os.getenv("AIRFLOW_MIN_PUBLISH_ATTEMPTS", "1")
        )
    else:
        assert states["gate"]["state"] in {"failed", "skipped"}
        assert states["publish"]["state"] in {"upstream_failed", "skipped"}


@pytest.mark.writes
def test_scheduler_retries_publish_after_side_effect_without_retraining(
    live_run, retry_evidence
):
    states, folder, run_id = live_run(fail_publish_once=True)
    assert all(row["state"] == "success" for row in states.values())
    evidence = retry_evidence(run_id)
    attempts = evidence["attempts"]
    assert attempts["publish"] == 2
    assert attempts["train_evaluate"] == attempts["validate_data"] == 1
    releases = list((folder / "releases").glob("*.json"))
    assert len(releases) == 1
    release = json.loads(releases[0].read_text())
    assert releases[0].stem == release["run_key"]
    assert_publication_precedes_failure(releases[0].stat().st_mtime, evidence)


@pytest.mark.writes
def test_scheduler_gate_rejection_never_publishes(live_run):
    states, folder, _ = live_run(gate_ratio=0.0)
    assert states["train_evaluate"]["state"] == "success"
    assert states["gate"]["state"] == "failed"
    assert states["publish"]["state"] == "upstream_failed"
    assert not list((folder / "releases").glob("*.json"))


def assert_publication_precedes_failure(release_mtime, evidence):
    assert (
        release_mtime <= evidence["first_failure_at"] < evidence["second_started_at"]
    ), "Release must exist before first failure and remain unchanged on retry"

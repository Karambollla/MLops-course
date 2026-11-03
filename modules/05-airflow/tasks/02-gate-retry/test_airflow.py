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

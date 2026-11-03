"""Check actual scheduler intervals of two explicitly selected learner DAG runs."""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("MLOPS_RUN_INTEGRATION") != "1",
        reason="Two completed learner Airflow runs required",
    ),
]


def test_two_real_dag_runs_have_distinct_daily_intervals():
    run_ids = json.loads(os.environ["AIRFLOW_INTERVAL_RUN_IDS"])
    assert isinstance(run_ids, list) and len(run_ids) == len(set(run_ids)) == 2
    script = """
import json, sys
from airflow.models.dagrun import DagRun
from airflow.utils.session import create_session
with create_session() as session:
    runs = session.query(DagRun).filter(DagRun.dag_id == "housing_pipeline", DagRun.run_id.in_(json.loads(sys.argv[1]))).all()
    print(json.dumps([{"run_id": run.run_id, "state": run.state, "start": run.data_interval_start.isoformat() if run.data_interval_start else None, "end": run.data_interval_end.isoformat() if run.data_interval_end else None} for run in runs]))
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
            json.dumps(run_ids),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    rows = json.loads(result.stdout.strip().splitlines()[-1])
    assert {row["run_id"] for row in rows} == set(run_ids)
    starts = set()
    for row in rows:
        assert row["state"] == "success"
        start, end = (
            datetime.fromisoformat(row["start"]),
            datetime.fromisoformat(row["end"]),
        )
        assert start.utcoffset() == end.utcoffset() == timedelta(0)
        assert end - start == timedelta(days=1)
        assert (start.hour, start.minute, start.second, start.microsecond) == (
            0,
            0,
            0,
            0,
        )
        starts.add(start)
    assert len(starts) == 2

"""Shared preparation for real Task SDK and explicitly enabled live runs."""

import csv
import json
import random
import tempfile
import time
import uuid
import os
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import pytest
from course_tasks import course_root, load_task


try:
    import airflow
    from airflow.sdk import DAG
    from airflow.timetables.interval import CronDataIntervalTimetable
except ModuleNotFoundError as error:
    if error.name != "airflow":
        raise
    airflow = DAG = CronDataIntervalTimetable = None


@pytest.fixture
def airflow_sdk():
    if os.getenv("MLOPS_RUN_SDK") != "1":
        pytest.skip("Set MLOPS_RUN_SDK=1 inside the labs/airflow container")
    if airflow is None:
        pytest.fail("Airflow SDK required: run this test in the labs/airflow container")
    assert airflow.__version__ == "3.1.0"
    return airflow


@pytest.fixture
def dag_type(airflow_sdk):
    return DAG


@pytest.fixture
def timetable_type(airflow_sdk):
    return CronDataIntervalTimetable


@pytest.fixture
def build(airflow_sdk):
    return load_task("05-airflow/01-pipeline").build_dag


@pytest.fixture
def sample_csv():
    """Deterministic small CSV, generated without ML dependencies or downloads."""

    def write(path):
        rng = random.Random(17)
        with Path(path).open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                [
                    "MedInc",
                    "HouseAge",
                    "AveRooms",
                    "AveBedrms",
                    "Population",
                    "AveOccup",
                    "Latitude",
                    "Longitude",
                    "MedHouseVal",
                ]
            )
            for _ in range(200):
                income = rng.uniform(1, 10)
                writer.writerow(
                    [
                        income,
                        20,
                        5,
                        1,
                        1000,
                        3,
                        35,
                        -120,
                        0.4 * income + rng.uniform(-0.1, 0.1),
                    ]
                )
        return Path(path)

    return write


@pytest.fixture
def execute_dag(airflow_sdk, tmp_path, sample_csv):
    """Run learner DAG using real SDK/execution API with isolated metadata DB."""

    def execute(stage, *, logical_date="2025-01-02T00:00:00+00:00", **overrides):
        folder = tmp_path / str(len(list(tmp_path.iterdir())))
        folder.mkdir()
        data = sample_csv(folder / "data.csv")
        conf = {
            "data_path": str(data),
            "seed": 17,
            "output_root": str(folder / "runs"),
            "release_dir": str(folder / "releases"),
            **overrides,
        }
        script = textwrap.dedent("""
            import json, sys
            from datetime import datetime
            from airflow.utils import db
            from airflow.cli.commands.dag_command import get_bagged_dag
            db.initdb()
            dag = get_bagged_dag(bundle_names=None, dag_id="housing_pipeline", dagfile_path="/opt/airflow/dags/housing_pipeline.py")
            run = dag.test(logical_date=datetime.fromisoformat(sys.argv[2]), run_after=datetime.fromisoformat(sys.argv[2]), run_conf=json.loads(sys.argv[3]))
            rows = run.get_task_instances()
            values = {}
            for ti in rows:
                if ti.state == "success":
                    values[ti.task_id] = ti.xcom_pull(task_ids=ti.task_id, key="return_value")
            print("COURSE_DAG_RESULT=" + json.dumps({"state": run.state, "tasks": {ti.task_id: {"state": ti.state, "attempts": ti.try_number} for ti in rows}, "xcom": values}))
        """)
        env = {
            **os.environ,
            "AIRFLOW_HOME": str(folder / "airflow"),
            "MLOPS_AIRFLOW_STAGE": str(stage),
            "AIRFLOW__CORE__DAGS_FOLDER": "/opt/airflow/dags",
            "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": f"sqlite:///{folder / 'airflow.db'}",
            "AIRFLOW__CORE__LOAD_EXAMPLES": "false",
            "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION": "true",
        }
        result = subprocess.run(
            ["python", "-c", script, str(stage), logical_date, json.dumps(conf)],
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert result.returncode == 0, (result.stdout + result.stderr)[-16000:]
        lines = [
            line.removeprefix("COURSE_DAG_RESULT=")
            for line in result.stdout.splitlines()
            if line.startswith("COURSE_DAG_RESULT=")
        ]
        assert len(lines) == 1, result.stdout[-10000:]
        return json.loads(lines[0]), folder

    return execute


@pytest.fixture
def airflow_cli():
    """Observe the existing course container; no implicit up/down or task clearing."""
    root = course_root()

    def cli(*args):
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(root / "labs/airflow/compose.yaml"),
                "exec",
                "-T",
                "airflow",
                "airflow",
                *args,
            ],
            text=True,
            capture_output=True,
            timeout=30,
            check=True,
        )
        return result.stdout

    return cli


@pytest.fixture
def live_run(airflow_cli, sample_csv):
    """Explicit writes: unique run IDs/files, never delete unrelated metadata."""
    if (
        os.getenv("MLOPS_RUN_INTEGRATION") != "1"
        or os.getenv("MLOPS_RUN_WRITES") != "1"
    ):
        pytest.skip("Set both MLOPS_RUN_INTEGRATION=1 and MLOPS_RUN_WRITES=1")
    root = course_root()
    (root / "work").mkdir(exist_ok=True)

    def run(*, stage=2, **overrides):
        current = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(root / "labs/airflow/compose.yaml"),
                "exec",
                "-T",
                "airflow",
                "printenv",
                "MLOPS_AIRFLOW_STAGE",
            ],
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
        assert current.stdout.strip() == str(stage), (
            f"Recreate course container with MLOPS_AIRFLOW_STAGE={stage}"
        )
        definitions = json.loads(airflow_cli("dags", "list", "-o", "json"))
        selected = next(
            row for row in definitions if row["dag_id"] == "housing_pipeline"
        )
        assert selected["is_paused"] is False, (
            "Unpause the prepared course DAG before live tests"
        )
        folder = Path(tempfile.mkdtemp(prefix="airflow-acceptance-", dir=root / "work"))
        sample_csv(folder / "data.csv")
        remote = "/work/" + folder.name
        conf = {
            "data_path": remote + "/data.csv",
            "seed": 17,
            "output_root": remote + "/runs",
            "release_dir": remote + "/releases",
            **overrides,
        }
        run_id = "course-acceptance-" + uuid.uuid4().hex
        arguments = ["dags", "trigger", "--run-id", run_id, "--conf", json.dumps(conf)]
        if stage == 3:
            arguments += [
                "--logical-date",
                acceptance_logical_date(),
                "--no-replace-microseconds",
            ]
        airflow_cli(*arguments, "housing_pipeline")
        deadline = time.monotonic() + 150
        states = []
        while time.monotonic() < deadline:
            states = json.loads(
                airflow_cli(
                    "tasks",
                    "states-for-dag-run",
                    "housing_pipeline",
                    run_id,
                    "-o",
                    "json",
                )
            )
            if len(states) >= (5 if stage == 3 else 4) and all(
                row["state"] in {"success", "failed", "upstream_failed", "skipped"}
                for row in states
            ):
                return {row["task_id"]: row for row in states}, folder, run_id
            time.sleep(1)
        pytest.fail(f"Run {run_id} did not finish: {states}")

    yield run
    # Keep files: the scheduler's DagRun/XCom refer to them for inspection.
    # No automatic metadata deletion or removal of active task resources.


def acceptance_logical_date() -> str:
    """Unique control timestamp, not the learner's way to derive a partition."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=uuid.uuid4().int % 1000000)
        .isoformat()
    )


@pytest.fixture
def retry_evidence():
    root = course_root()

    def observe(run_id):
        script = """
import json,sys
from airflow.models.taskinstance import TaskInstance
from airflow.models.taskinstancehistory import TaskInstanceHistory
from airflow.models.dagrun import DagRun
from airflow.utils.session import create_session
with create_session() as session:
    rows=session.query(TaskInstance).filter(TaskInstance.dag_id=='housing_pipeline', TaskInstance.run_id==sys.argv[1]).all()
    first=session.query(TaskInstanceHistory).filter(TaskInstanceHistory.dag_id=='housing_pipeline', TaskInstanceHistory.run_id==sys.argv[1], TaskInstanceHistory.task_id=='publish', TaskInstanceHistory.try_number==1).one()
    current=next(row for row in rows if row.task_id=='publish')
    run=session.query(DagRun).filter(DagRun.dag_id=='housing_pipeline', DagRun.run_id==sys.argv[1]).one()
    print(json.dumps({'attempts':{row.task_id:row.try_number for row in rows}, 'first_failure_at':first.end_date.timestamp(), 'second_started_at':current.start_date.timestamp(), 'start':run.data_interval_start.isoformat() if run.data_interval_start else None, 'end':run.data_interval_end.isoformat() if run.data_interval_end else None}))
"""
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
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
        return json.loads(result.stdout.strip().splitlines()[-1])

    return observe

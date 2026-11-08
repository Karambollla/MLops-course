"""Real timetable and context, not manually supplied strings or callbacks."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from course_tasks import load_task

pytestmark = pytest.mark.sdk


def test_real_daily_timetable_and_context_dependency(build, timetable_type):
    s = load_task("05-airflow/03-failure-intervals")
    schedule = s.daily_schedule()
    assert isinstance(schedule, timetable_type)
    dag = build(3)
    assert isinstance(dag.timetable, timetable_type)
    assert dag.catchup is False and dag.max_active_runs == 1
    assert set(dag.task_ids) == {
        "prepare_interval",
        "validate_data",
        "train_evaluate",
        "gate",
        "publish",
    }
    assert dag.get_task("prepare_interval").downstream_task_ids == {"validate_data"}
    interval = dag.timetable.infer_manual_data_interval(
        run_after=datetime(2025, 1, 2, tzinfo=timezone.utc)
    )
    assert interval.start.isoformat() == "2025-01-01T00:00:00+00:00"
    assert interval.end.isoformat() == "2025-01-02T00:00:00+00:00"


def test_two_real_contexts_produce_distinct_training_outputs(execute_dag):
    outputs = []
    for date in ("2025-01-02T00:00:00+00:00", "2025-01-03T00:00:00+00:00"):
        result, _ = execute_dag(3, logical_date=date)
        assert result["state"] == "success", result
        metadata = result["xcom"]["train_evaluate"]
        saved = json.loads((Path(metadata["path"]) / "orchestration.json").read_text())
        interval = saved["interval"]
        assert interval == result["xcom"]["prepare_interval"]
        assert saved["run_key"] == metadata["run_key"]
        assert saved["model_version"] == metadata["model_version"]
        outputs.append((metadata, interval))
    assert outputs[0][0]["run_key"] != outputs[1][0]["run_key"]
    assert outputs[0][0]["path"] != outputs[1][0]["path"]
    assert outputs[0][1]["data_interval_end"] == outputs[1][1]["data_interval_start"]

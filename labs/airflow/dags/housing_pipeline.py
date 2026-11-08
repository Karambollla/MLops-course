"""Airflow entrypoint: load the learner's factory for the selected stage."""

import os

from course_tasks import load_task

stage = int(os.getenv("MLOPS_AIRFLOW_STAGE", "1"))
dag = load_task("05-airflow/01-pipeline").build_dag(stage)

# Workers reload the registered entrypoint, not the factory module outside the DAG bundle.
dag.fileloc = __file__

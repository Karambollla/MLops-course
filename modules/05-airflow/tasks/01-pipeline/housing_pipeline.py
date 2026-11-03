"""Учебный DAG: scheduler импортирует только Airflow и stdlib.

Task starter сознательно падает NotImplementedError до реализации solution.py.
"""

# ruff: noqa: F401
# Контекст и timetable подготовлены для заданий об интервалах и восстановлении.

import hashlib
import json
import subprocess
from pathlib import Path

import pendulum
from airflow.sdk import dag, get_current_context, task
from airflow.timetables.interval import CronDataIntervalTimetable


@dag(
    dag_id="housing_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    tags=["course"],
)
def housing_pipeline():
    @task(retries=1)
    def validate_data() -> str:
        path = Path("/work/housing.csv")
        if not path.is_file():
            raise FileNotFoundError("Сначала скачай work/housing.csv на host")
        return str(path)

    @task(retries=1)
    def train_evaluate(data_path: str) -> dict:
        # TODO(student): включи версию кода и полную конфигурацию в run_key.
        digest = hashlib.sha256(Path(data_path).read_bytes()).hexdigest()
        run_key = hashlib.sha256((digest + ":seed=42:starter-v1").encode()).hexdigest()[
            :24
        ]
        output = "/work/runs/" + run_key
        # Выполняется внутри ML venv; scheduler не импортирует sklearn.
        script = (
            "import json,sys; from course_tasks import load_task; "
            'm=load_task("05-airflow/01-pipeline"); '
            "result=m.run_training(sys.argv[1],sys.argv[2],42); "
            "print(json.dumps(result))"
        )
        try:
            completed = subprocess.run(
                ["/opt/housing-venv/bin/python", "-c", script, data_path, output],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                "Обучение завершилось ошибкой:\n" + (error.stderr or "")
            ) from error
        # Training CLI может печатать логи; последняя строка — metadata JSON.
        result = json.loads(completed.stdout.strip().splitlines()[-1])
        if set(result) != {"path", "run_key"}:
            raise ValueError("XCom должен содержать только path и run_key")
        return result

    @task(retries=1)
    def gate(metadata: dict) -> dict:
        # TODO(student, тема 02): прочитай metrics.json по metadata["path"].
        # Вызови свою quality_gate через ML venv; явно запрети publish при false.
        # XCom возвращает только маленькие metadata, не модель и не DataFrame.
        raise NotImplementedError("Подключи quality gate к настоящей Airflow task")

    @task(retries=1)
    def publish(metadata: dict) -> dict:
        # TODO(student, темы 02/03): вызови свой идемпотентный publish через ML venv.
        # get_current_context() даёт dag_run/ti и data_interval_start/end:
        # сохрани реальный interval в manifest и исходный run_key при retry.
        # Верни только metadata точного release, проверь файлы после side effect.
        raise NotImplementedError("Подключи публикацию к настоящей Airflow task")

    # TODO(student, тема 03): замени schedule=None явным UTC data-interval timetable,
    # включи interval + версию кода/конфигурацию в смысловой ключ и manifest.
    publish(gate(train_evaluate(validate_data())))


housing_pipeline()

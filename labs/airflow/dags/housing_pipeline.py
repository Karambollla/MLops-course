"""DAG импортируется; учебная task падает до самостоятельной реализации."""
import pendulum
from airflow.sdk import dag, task

@dag(dag_id="housing_pipeline", schedule=None,
     start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
     catchup=False, max_active_runs=1, tags=["course"])
def housing_pipeline():
    @task(retries=1)
    def validate_data() -> str:
        from pathlib import Path
        path = Path("/work/housing.csv")
        if not path.is_file():
            raise FileNotFoundError("Сначала скачай work/housing.csv на host")
        return str(path)

    @task(retries=1)
    def train_evaluate(data_path: str) -> dict:
        # TODO(student): existing train -> gate -> idempotent release manifest.
        raise NotImplementedError("Реализуй обучение, gate и публикацию по модулю 05")

    train_evaluate(validate_data())

housing_pipeline()

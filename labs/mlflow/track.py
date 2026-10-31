"""Упражнение 04: реальный train и регистрация, без фиктивных метрик."""
import os
import mlflow
mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
mlflow.set_experiment("housing-course")

def main():
    # TODO(student): три конфигурации; log metrics/artifacts/model; aliases.
    raise NotImplementedError("Подключи свой train и сравнение конфигураций")

if __name__ == "__main__":
    main()

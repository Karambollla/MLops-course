# DAG без подмены обучения

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Редактируй `modules/05-airflow/tasks/01-pipeline/solution.py` (физическая заготовка рядом). Дополнительные тесты размещай в этой же папке. Полных решений в заготовке нет.

`run_training(data_path: str | Path, output_path: str | Path, seed: int = 42) -> dict`: вызови существующий housing.train в ML venv через subprocess.run с массивом аргументов и check=True; никаких shell=True. Возвращает только {path: str(output_path), run_key: output_path.name}, после проверки наличия всех четырёх артефактов. Не заменяй обучение фиктивными файлами. Редактируй solution.py и housing_pipeline.py в этой папке. DAG mounted parent-инфраструктурой; путь данных /work/housing.csv, output /work/runs/RUN_KEY. Ключ стабилен от SHA CSV, seed/config и версии кода, не от времени. DAG schedule=None, catchup=False, max_active_runs=1, retries=1; top-level не импортирует sklearn. Через XCom только путь/run_key. До реализации ожидается NotImplementedError в task, а не import error. Gate и publish добавляются из следующего задания.

## Среда и зависимости

Базовая среда из SETUP: Python, pytest; CPU, Linux/macOS.

Зависит от 01-ml/02-candidate, манифеста и MLflow. Офлайн-тест перехватывает CLI, реальный DAG проверяй compose list-import-errors/unpause/trigger/list-runs. Docker Desktop и Airflow нужны только для этого. Обучение должно произойти в ML venv, scheduler не импортирует модельные библиотеки.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=05-airflow/01-pipeline
```

До реализации ожидается RED: `NotImplementedError`, а не ошибка импорта зависимостей. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

Это задание использует функции; импортируй заготовку через `course_tasks.load_task("05-airflow/01-pipeline")` из Python. CLI не требуется.

## Требования практического опыта

В `housing_pipeline.py` рядом с `solution.py` реализуй task `train_evaluate`. Рабочие данные внутри контейнера доступны в `/work`; пакет housing уже установлен из исходников при сборке. Создай результат в `/work/runs/RUN_KEY`, передай через XCom только путь и run_key. До реализации task ожидаемо падает.

```bash
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags list-import-errors
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags unpause housing_pipeline
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags trigger housing_pipeline
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags list-runs housing_pipeline
```

Новый DAG по умолчанию paused. Команда unpause разрешает scheduler запускать задачи; trigger без неё может оставить run в queued. После trigger повтори list-runs через несколько секунд и проверь переход в running, затем success после реализации или ожидаемый failed с учебным исключением до неё. Пустая таблица означает, что run не создан или выбран другой DAG.

У учебной task задан `retries=1`; стандартная пауза перед повтором составляет пять минут. Поэтому после первого NotImplementedError можно увидеть `up_for_retry`, пока DAG run ещё running. Смотри состояние и логи конкретной task, а не только общий статус DAG.

## Приёмка и очистка

Выполни `test_task.py`: проверяются результаты функций, ошибки входа и изменения технических артефактов. Письменный пересказ выполнения не требуется.

После опыта останови стенд: `docker compose -f labs/airflow/compose.yaml down`. Uvicorn останови Ctrl+C. Не удаляй volume без экспорта истории; артефакты `work/` сохрани для следующих модулей.

## Пример корректного результата

В DAG validate_data завершается success, train_evaluate запускает housing.train в ML venv. XCom содержит только path и run_key. До реализации обучения ожидается NotImplementedError из заготовки; import error DAG или отсутствие данных — отдельные ошибки подготовки.

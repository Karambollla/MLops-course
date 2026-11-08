# Построить DAG обучения через Task SDK

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

Существующая `housing.train` уже умеет обучать модель. Теперь нужно описать, когда её вызывать и как передать результат следующей работе. В [solution.py](solution.py) реализуй фабрику настоящего DAG. Здесь ты сам применяешь `@dag`, `@task`, `Param` и `get_current_context` из `airflow.sdk`.

Первый этап заканчивается двумя успешно выполненными задачами: `validate_data → train_evaluate`. Gate и публикация пока не нужны. Различие описания и выполнения разобрано в [теории TaskFlow](../../README.md#как-функция-становится-задачей).

## Что подготовлено

[Загрузчик](../../../../labs/airflow/dags/housing_pipeline.py) только вызывает твою `build_dag`. Готовый [runtime](../../../../labs/housing/src/housing/airflow_runtime.py) запускает сохранённое обучение в отдельной ML-среде и проверяет результат. Реализовывать subprocess в этом задании не нужно.

Сначала заверши ML-notebook, сохрани его и подготовь CSV `work/housing.csv`. Импорты уже предоставлены в заготовке. Если SDK отсутствует на host, используй контейнер из [подготовки модуля](../../README.md#подготовка-к-заданиям).

## Интерфейс и настройки DAG

```python
def build_dag(stage: int = 1) -> DAG:
    ...
```

| Аргумент | Тип и источник | Назначение |
|---|---|---|
| `stage` | `int`: 1, 2 или 3. Загрузчик читает `MLOPS_AIRFLOW_STAGE`, default 1 | Выбирает состав графа при разборе файла, а не конфигурацию будущей задачи |

Верни настоящий объект `airflow.sdk.DAG`. Внутри `build_dag` создай фабрику с `@dag` и вызови её. Имя графа — `housing_pipeline`. Для этапа 1 задай `schedule=None`, `start_date=datetime(2025, 1, 1, tzinfo=timezone.utc)`, `catchup=False`, `max_active_runs=1`. У задач первого этапа задай `retries=0`, чтобы ошибка входа не превращалась в долгий повтор.

Создай следующие DAG-level Params. Значения путей относятся к файловой системе контейнера:

| Имя | Default | Схема и смысл |
|---|---|---|
| `data_path` | `/work/housing.csv` | `type="string"`, путь CSV |
| `seed` | `42` | `type="integer"`, настройка обучения |
| `output_root` | `/work/runs` | `type="string"`, родитель папок отдельных обучений |

Выполнение тестов переопределяет пути временными каталогами. Не зашивай `/work/runs` в тело задачи вместо чтения параметров. Настройки конкретного запуска бери через `get_current_context()["params"]` только внутри задачи.

## Задача validate_data

Создай её декоратором `@task` с `task_id="validate_data"`. Подготовь необязательный аргумент `interval=None`: в первом этапе он не передаётся, в третьем получит результат задачи интервала.

Внутри задачи прочитай параметры запуска и вызови готовую функцию:

```python
def prepare_training(data_path, seed=42, *, output_root="/work/runs", interval=None) -> dict:
    ...
```

| Аргумент helper | Откуда взять | Пример |
|---|---|---|
| `data_path` | Runtime Param `data_path` | `/work/housing.csv` |
| `seed` | Runtime Param `seed` | `17` |
| `output_root` | Runtime Param `output_root` | `/work/runs` |
| `interval` | В первом этапе `None`. Позже вход задачи через XCom | `None` |

Helper проверяет непустой файл и seed, рассчитывает SHA данных и исходников обучения, затем устойчивый ключ. Он возвращает конфигурацию: `data_path`, `seed`, `data_sha256`, `code_revision`, `interval`, `run_key`, `path`. При отсутствии CSV возникает `FileNotFoundError`, при неверном seed — `ValueError`. Не вызывай его во время построения DAG.

## Задача train_evaluate

Создай `@task` с `task_id="train_evaluate"`. Её аргумент — конфигурация, возвращённая `validate_data`. Внутри задачи вызови готовую `run_training(configuration: dict) -> dict` и верни результат.

Helper запускает твою `train` в `/opt/housing-venv`, проверяет четыре файла и читает `model_version` из доверенного bundle внутри ML-среды. Результат содержит ровно три поля:

```json
{"path":"/work/runs/example-key","run_key":"example-key","model_version":"собственная-версия-модели"}
```

Строки выше показывают формат, настоящие значения вычисляет обучение. Ошибка ML-процесса, неполный комплект файлов или изменившиеся после проверки данные завершают задачу ошибкой. Не подменяй результат фиктивными метриками или моделью.

Свяжи задачи передачей TaskFlow-результата `validate_data` в `train_evaluate`. Модель не возвращается через XCom. Первый этап не должен загружать или вызывать `attach_release` и `attach_interval_context` незавершённых заданий.

## Проверка SDK

После реализации запусти в контейнере:

```bash
docker compose -f labs/airflow/compose.yaml exec -T -e MLOPS_RUN_SDK=1 airflow python -m pytest /course/modules/05-airflow/tasks/01-pipeline/test_task.py -q
```

Проверяется настоящий DAG, отсутствие обучения при построении, чтение seed конкретного запуска, четыре файла, небольшой XCom и отказ отсутствующего CSV. Исполняемые проверки вызывают сохранённые функции notebook на синтетических данных в изолированной среде Airflow. Незавершённые функции предыдущего модуля вызывают реальную ошибку, а не пропуск.

На host `make task TASK=05-airflow/01-pipeline` без флага SDK соберёт и пропустит эти проверки. Это не подтверждение выполнения задания.

## Запуск через scheduler

```bash
export MLOPS_AIRFLOW_STAGE=1
docker compose -f labs/airflow/compose.yaml up -d --build
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags list-import-errors
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags unpause housing_pipeline
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags trigger --conf '{"seed":17}' housing_pipeline
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags list-runs housing_pipeline
```

Запиши идентификатор нужного запуска из CLI или UI. Открой его задачи: обе должны стать `success`, весь DagRun тоже должен завершиться успешно. В XCom `train_evaluate` найди путь и сопоставь его с `work/runs/` на host. В `manifest.json` должен быть seed 17.

Если run остаётся queued, проверь, что DAG снят с паузы и scheduler работает. Если импорт падает на `NotImplementedError`, реализация фабрики ещё не сохранена или не завершена. Если падает ML-процесс, проверь сохранённый notebook и четыре ожидаемых файла.

## Завершение

Сохрани код и результаты для второго задания. При перерыве останови стенд через `docker compose -f labs/airflow/compose.yaml down`. Папки обучения и история в volume сохраняются.

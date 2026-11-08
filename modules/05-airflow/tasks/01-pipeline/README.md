# DAG без подмены обучения

[Модуль и подготовка](../../README.md#подготовка-к-заданиям) · [Все задания модуля](../../README.md#задания) · [SETUP](../../../../SETUP.md)

## Что предстоит сделать

У тебя уже есть CLI с проверенной процедурой split/fit/evaluate. Теперь реализуй `run_training` в соседнем [solution.py](solution.py) и доработай ключ запуска в [housing_pipeline.py](housing_pipeline.py). Шаг графа должен вызвать прежнее обучение, проверить его файлы и передать следующему шагу путь к ним. Результат проверяется сначала тестом функции, затем по выполнению `train_evaluate` в Airflow. Роли процессов и окружений показаны в [архитектуре графа](../../README.md#кто-исполняет-граф-и-кто-исполняет-обучение), путь результата — в [разборе запуска](../../README.md#один-запуск-от-csv-до-xcom).

## Что подготовлено

Нужны реализованный [train кандидата](../../../01-ml/housing.ipynb), манифест и host-файл `work/housing.csv`. Compose отображает его в `/work/housing.csv`. Образ содержит пакет housing и отдельный ML venv. В `housing_pipeline.py` уже заданы validate_data, вызов ML-процесса и начальные настройки. Реализуй `run_training`, доработай устойчивый ключ и подключи обучение. После правки solution.py пересобери image. DAG-файл монтируется отдельно и обновляется иначе.

Для пояснения обозначим устойчивый ключ одного обучения как `key-1`, а его каталог — `/work/runs/key-1`. Если output равен этому пути, правильный subprocess получает этот путь одним аргументом, выполняет `housing.train` и создаёт четыре файла. Только после их проверки функция возвращает `{"path":"/work/runs/key-1","run_key":"key-1"}`. Если процесс вернул код 1, функция должна сообщить об ошибке, а не выдавать metadata успешного результата. Offline-тест перехватывает subprocess и проверяет контракт. Настоящее обучение и статус task подтверждаются отдельно в Airflow.

## `run_training`: вызвать CLI и проверить файлы

```python
def run_training(
    data_path: str | Path, output_path: str | Path, seed: int = 42
) -> dict:
    ...
```

| Параметр | Тип | Формат и смысл | Откуда берётся | Пример |
|---|---|---|---|---|
| `data_path` | `str` или `Path` | Путь к существующему housing CSV в файловой системе процесса обучения | Возвращает `validate_data` DAG | `"/work/housing.csv"` |
| `output_path` | `str` или `Path` | Каталог четырёх результатов. Последняя часть имени является `run_key` | DAG формирует его из устойчивого ключа | `Path("/work/runs/key-1")` |
| `seed` | `int`, по умолчанию `42` | Настройка случайных операций существующего train | Конфигурация запуска | `17` |

Функция запускает `/opt/housing-venv/bin/python -m housing.train` через `subprocess.run`. Передай `--data`, `--output` и `--seed` отдельными элементами массива аргументов. Нужны `check=True` и выполнение без `shell=True`. Например, путь `"/work/input with spaces.csv"` должен остаться одним аргументом. В тесте проверяются ровно эти три CLI-настройки.

После кода 0 проверь наличие `model.joblib`, `metrics.json`, `manifest.json`, `split.json` в output. Только тогда верни словарь:

```python
# При output_path == Path("/work/runs/key-1"):
{"path": "/work/runs/key-1", "run_key": "key-1"}
```

Иных полей в XCom train нет. Это указатель на результат, а не содержимое модели. Ошибка CLI пробрасывается как `subprocess.CalledProcessError`. Если процесс завершился успешно, но не создал один из файлов, функция должна завершиться ошибкой. Проверки допускают `FileNotFoundError`, `ValueError` или `RuntimeError` для такого неполного output. Не создавай фиктивные файлы вместо обучения. Быстрый тест подменяет subprocess и проверяет только этот контракт.

## Настройки и данные DAG

`housing_pipeline.py` — описание графа. Не импортируй sklearn и не запускай обучение на верхнем уровне: scheduler читает файл при разборе DAG. ML-окружение отделено от Airflow и вызывается только внутри task.

| Поле или шаг | Исходное значение и смысл | Что сделать |
|---|---|---|
| `dag_id` | `housing_pipeline`, имя графа для UI и CLI | Использовать это имя в командах ниже |
| `schedule`, `catchup` | `None`, `False`: ручной запуск без создания прошлых интервалов | Сохранить для первого опыта. Расписание добавляется в теме 03 |
| `max_active_runs` | `1`, одновременно выполняется один DAG run | Не запускать конкурирующие опыты с одним output |
| `retries` у task | `1`, одна повторная попытка после первой неудачи | Проверять конкретную попытку и её логи |
| `validate_data()` | Проверяет `/work/housing.csv`, возвращает строковый путь | Подготовить файл на host в `work/` |
| `train_evaluate(data_path)` | Запускает учебный `run_training` отдельным ML-процессом | Доработать ключ и проверить полученные `{path, run_key}` |
| `run_key` | В заготовке основан на SHA CSV, seed и строке `starter-v1` | Включить действительную версию кода и полную конфигурацию. Ключ не зависит от времени попытки |
| `output` | `/work/runs/RUN_KEY` | Отдельный каталог каждого смыслового запуска |
| `gate(metadata)`, `publish(metadata)` | Уже связаны в граф, тела пока поднимают `NotImplementedError` | Подключить функции тем 02–03 |

Путь `/work` — общий mount учебного контейнера. На нескольких workers локальный каталог сам по себе не станет общим: понадобится доступное всем хранилище. `metadata` между шагами остаётся небольшим JSON с путём и ключом. Ошибки разбора DAG проверяй до trigger: наличие файла в папке ещё не означает успешный импорт.

## Проверка функции

Из корня курса в [основной среде](../../../../SETUP.md#основная-среда):

```bash
make task TASK=05-airflow/01-pipeline
```

[test_task.py](test_task.py) подменяет subprocess и проверяет аргументы, обработку кода завершения и полноту файлов. До реализации ожидается `NotImplementedError`. Для вызова из Python используй `course_tasks.load_task("05-airflow/01-pipeline")`. Отдельного CLI у заготовки нет.

## Требования практического опыта

Пересобери стенд после правки `solution.py` по [подготовке модуля](../../README.md#подготовка-к-заданиям). В `housing_pipeline.py` уже есть вызов ML-процесса. Проверь его результат после своей реализации `run_training` и доработки ключа. Следующие `gate` и `publish` пока могут оставаться заготовками тем 02–03.

```bash
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags list-import-errors
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags unpause housing_pipeline
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags trigger housing_pipeline
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags list-runs housing_pipeline
```

Новый DAG по умолчанию paused. Команда unpause разрешает scheduler запускать задачи. trigger без неё может оставить run в queued. После trigger повтори list-runs через несколько секунд и проверь переход в running. Открой task instance `train_evaluate`: после реализации она должна завершиться success и сохранить четыре файла. Весь DagRun станет success только после реализации следующих `gate` и `publish`. До этого их учебное исключение ожидаемо. Пустая таблица означает, что run не создан или выбран другой DAG.

У учебной task задан `retries=1`. Стандартная пауза перед повтором составляет пять минут. Поэтому после первого NotImplementedError можно увидеть `up_for_retry`, пока DAG run ещё running. Смотри состояние и логи конкретной task, а не только общий статус DAG.

## Настоящий SDK и загрузка DAG

`housing_pipeline.py` импортирует декораторы и context из `airflow.sdk` (Airflow 3.1.0). Отдельные `gate` и `publish` уже видны в графе как **заготовки действий**: их тела оставлены с `NotImplementedError`, реализуй их по темам 02/03. Передача metadata по зависимостям не заменяет проверку качества и публикацию.

Когда контейнер уже запущен, проверь импорт настоящим Airflow внутри него:

```bash
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/05-airflow/tasks/01-pipeline/test_task.py -m integration -q
```

Эта read-only проверка не поднимает контейнеры и не запускает tasks: настоящий `DagBag` проверяет импорт SDK, task IDs, зависимости и retry. Успешный импорт **не означает** выполненное обучение. Временные metadata `{path, run_key}` — контракт XCom train. Содержимое joblib/DataFrame туда не передаётся. Реальное выполнение всего DAG до реализации новых tasks ожидаемо падает с `NotImplementedError`.

После реализации функций и DAG используй существующий учебный стенд:

```bash
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags test housing_pipeline 2025-01-01T00:00:00+00:00
```

Команда исполняет tasks и пишет реальные DAG/task metadata и файлы в `/work`. Выбери отдельный output для опыта. Команда приведена в [CLI Airflow 3.1.0](https://airflow.apache.org/docs/apache-airflow/3.1.0/cli-and-env-variables-ref.html). `dags test` помогает отладке, но работа scheduler/retry и двух прошлых интервалов подтверждается отдельным опытом через UI по темам 02/03. Не используй mark-success, чтобы превратить невыполненный task в доказательство выполнения.

## Завершение

Сохрани файлы обучения и их `run_key` для следующей темы. Если прерываешь работу, останови стенд по [инструкции модуля](../../README.md#остановка-стенда). История в volume сохраняется.

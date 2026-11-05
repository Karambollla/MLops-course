# DAG без подмены обучения

[Модуль и подготовка](../../README.md#подготовка-к-заданиям) · [Все задания модуля](../../README.md#задания) · [SETUP](../../../../SETUP.md)

## Зачем графу вызывать существующее обучение

У тебя уже есть CLI с проверенной процедурой split/fit/evaluate. Оркестратор должен запускать этот код в нужном порядке и видеть его ошибку, а не создавать альтернативное «обучение» внутри DAG. Роли процессов и окружений показаны в [архитектуре графа](../../README.md#кто-исполняет-граф-и-кто-исполняет-обучение), путь результата — в [разборе запуска](../../README.md#один-запуск-от-csv-до-xcom).

## Что подготовлено

Нужны реализованный [train кандидата](../../../01-ml/housing.ipynb), манифест и host-файл `work/housing.csv`. Compose отображает его в `/work/housing.csv`. Образ содержит пакет housing и отдельный ML venv. В `housing_pipeline.py` уже заданы validate_data, вызов ML-процесса и начальные настройки. Реализуй `run_training`, доработай устойчивый ключ и подключи обучение. После правки solution.py пересобери image. DAG-файл монтируется отдельно и обновляется иначе.

Если output равен `/work/runs/key-1`, правильный subprocess получает этот путь одним аргументом, выполняет `housing.train` и создаёт четыре файла. Только после их проверки функция возвращает `{"path":"/work/runs/key-1","run_key":"key-1"}`. Если процесс вернул код 1, функция должна сообщить об ошибке, а не выдавать metadata успешного результата. Offline-тест перехватывает subprocess и проверяет контракт. Настоящее обучение и статус task подтверждаются отдельно в Airflow.

## Где работать

Реализуй `run_training` в [solution.py](solution.py) и доработай [housing_pipeline.py](housing_pipeline.py) рядом с ним. [Тесты](test_task.py) отдельно проверяют функцию и импорт графа настоящим SDK.

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

## Среда и зависимости

Для быстрых проверок используй основную среду Python с pytest из [SETUP](../../../../SETUP.md#основная-среда). Функции работают на CPU под Linux/macOS.

Зависит от ML-notebook модуля 01, манифеста и MLflow. Офлайн-тест перехватывает CLI, реальный DAG проверяй compose list-import-errors/unpause/trigger/list-runs. Docker Desktop и Airflow нужны только для этого. Обучение должно произойти в ML venv, scheduler не импортирует модельные библиотеки.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=05-airflow/01-pipeline
```

Тесты функций работают offline на маленьких входах и временных файлах. До реализации ожидается `NotImplementedError`. Ошибка импорта означает проблему подготовки среды. Проверка функций не заменяет описанный опыт на данных или стенде.

Это задание использует функции. Импортируй заготовку через `course_tasks.load_task("05-airflow/01-pipeline")` из Python. CLI не требуется.

## Требования практического опыта

В `housing_pipeline.py` рядом с `solution.py` реализуй task `train_evaluate`. Рабочие данные внутри контейнера доступны в `/work`. Пакет housing уже установлен из исходников при сборке. Создай результат в `/work/runs/RUN_KEY`, передай через XCom только путь и run_key. До реализации task ожидаемо падает.

```bash
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags list-import-errors
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags unpause housing_pipeline
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags trigger housing_pipeline
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags list-runs housing_pipeline
```

Новый DAG по умолчанию paused. Команда unpause разрешает scheduler запускать задачи. trigger без неё может оставить run в queued. После trigger повтори list-runs через несколько секунд и проверь переход в running, затем success после реализации или ожидаемый failed с учебным исключением до неё. Пустая таблица означает, что run не создан или выбран другой DAG.

У учебной task задан `retries=1`. Стандартная пауза перед повтором составляет пять минут. Поэтому после первого NotImplementedError можно увидеть `up_for_retry`, пока DAG run ещё running. Смотри состояние и логи конкретной task, а не только общий статус DAG.

## Приёмка и очистка

Запусти указанную выше команду `make task` после реализации и исправления ошибок. Проверяемые случаи перечислены в соседнем `test_task.py`.

После опыта останови стенд: `docker compose -f labs/airflow/compose.yaml down`. Не удаляй volume без экспорта истории. Артефакты `work/` сохрани для следующих модулей.

## Пример корректного результата

В DAG validate_data завершается success, train_evaluate запускает housing.train в ML venv. XCom содержит только path и run_key. До реализации обучения ожидается NotImplementedError из заготовки. import error DAG или отсутствие данных — отдельные ошибки подготовки.

## Настоящий SDK и загрузка DAG

`housing_pipeline.py` импортирует декораторы и context из `airflow.sdk` (Airflow
3.1.0). Отдельные `gate` и `publish` уже видны в графе как **заготовки действий**:
их тела оставлены с `NotImplementedError`, реализуй их по темам 02/03. Передача
metadata по зависимостям не заменяет проверку качества и публикацию.

Когда контейнер уже запущен, проверь импорт настоящим Airflow внутри него:

```bash
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/05-airflow/tasks/01-pipeline/test_task.py -m integration -q
```

Эта read-only проверка не поднимает контейнеры и не запускает tasks: настоящий
`DagBag` проверяет импорт SDK, task IDs, зависимости и retry. Успешный импорт
**не означает** выполненное обучение. Временные metadata `{path, run_key}` —
контракт XCom train. Содержимое joblib/DataFrame туда не передаётся. Реальное
выполнение всего DAG до реализации новых tasks ожидаемо падает с
`NotImplementedError`.

После реализации функций и DAG используй существующий учебный стенд:

```bash
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags test housing_pipeline 2025-01-01T00:00:00+00:00
```

Команда исполняет tasks и пишет реальные DAG/task metadata и файлы в `/work`.
Выбери отдельный output для опыта. Это ручное разрешение на запись. Автоматические
тесты с такой записью должны требовать **оба** `MLOPS_RUN_INTEGRATION=1` и
`MLOPS_RUN_WRITES=1`, markers `integration`, `writes`. Команда приведена в
[CLI Airflow 3.1.0](https://airflow.apache.org/docs/apache-airflow/3.1.0/cli-and-env-variables-ref.html).
`dags test` помогает отладке, но работа scheduler/retry и двух прошлых интервалов
подтверждается отдельным опытом через UI по темам 02/03. Не используй mark-success,
чтобы превратить невыполненный task в доказательство выполнения.

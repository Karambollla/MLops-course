# Добавить gate и настоящий повтор публикации

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Первый этап](../01-pipeline/README.md)

## Что предстоит сделать

Первый этап уже заканчивается обученной моделью. Теперь надо запретить выпуск плохого результата и пережить временный отказ после записи хорошего. В этом упражнении ты пишешь **задачи Airflow**, а не собственную машину состояний или цикл повторов.

В [solution.py](solution.py) реализуй `attach_release`. Затем подключи её в `build_dag` первого задания для `stage >= 2`. Итоговая цепочка: `validate_data → train_evaluate → gate → publish`. Отказ gate блокирует последний шаг, ошибка publish допускает настоящий retry. [Кто выполняет retry](../../README.md#кто-выполняет-retry).

## Подготовка и вход функции

Нужны завершённый первый этап и работающие функции notebook. Импорты SDK, `AirflowFailException`, `timedelta` и готовых helpers уже предоставлены.

```python
def attach_release(metadata: Any) -> Any:
    ...
```

| Аргумент | Во время построения графа | При выполнении задачи |
|---|---|---|
| `metadata` | TaskFlow-ссылка на результат `train_evaluate` | Словарь с `path`, `run_key`, `model_version`, полученный из XCom |

`Any` здесь отражает две стадии TaskFlow. Не нужно вручную декодировать ссылку при разборе DAG. Передай её задаче `gate`, а результат gate — задаче `publish`. Функция `attach_release` возвращает TaskFlow-ссылку результата publish. Вне активной фабрики DAG эту функцию не вызывают.

Добавь DAG-level Params в `build_dag`:

| Имя | Default и схема | Для чего нужно |
|---|---|---|
| `gate_ratio` | `0.9`, `type="number"`, `minimum=0`, `maximum=1` | Допустимое отношение test MAE кандидата к baseline |
| `fail_publish_once` | `False`, `type="boolean"` | Контролируемый сбой после записи на первой попытке |
| `release_dir` | `/work/releases`, `type="string"` | Папка файлов выпуска, временный путь в тестах |

Эти значения читаются через `get_current_context()["params"]` внутри соответствующей задачи. Этап 1 остаётся рабочим без загрузки этого компонента.

## Задача gate

Создай её через `@task` с `task_id="gate"`, `retries=0`. Вход — metadata обучения. Готовая функция `quality_gate(metadata: dict, ratio: float = 0.9) -> bool` читает `metrics.json` из `metadata["path"]` и сравнивает фактические test MAE:

`candidate.test.mae <= ratio * baseline.test.mae`

Например, для baseline=1.0 и candidate=0.8 default-порог 0.9 пройден. При candidate=0.95 модель не допускается. Это проверка выпуска уже выбранной модели, а не способ подбирать конфигурации по test. Некорректные или неконечные метрики вызывают `ValueError`.

Если helper вернул `False`, подними `AirflowFailException`. Если вернул `True`, верни неизменённый metadata следующей задаче. Просто вернуть `False` недостаточно: Airflow сочтёт обычное возвращение успешным выполнением.

## Задача publish

Создай `@task` с `task_id="publish"`, `retries=1`, `retry_delay=timedelta(seconds=1)`. Оставь стандартное правило `all_success`: после неуспешного gate задача не должна выполняться.

Внутри вызови `publish_release(metadata, release_dir)`. Папку получи из runtime Param. Helper записывает один файл `<run_key>.json` и возвращает словарь:

```json
{"run_key":"example-key","model_path":"/work/runs/example-key/model.joblib","model_version":"собственная-версия"}
```

Повтор с теми же полями возвращает прежний выпуск без перезаписи. Другая версия или путь при том же ключе вызывают `ValueError`. Отсутствующая модель не публикуется. Каждый файл записывается через временный файл и атомарную замену, без обещания общей распределённой транзакции.

После записи получи `get_current_context()["ti"].try_number`. Если `fail_publish_once=True` и это первая попытка, подними обычный `RuntimeError`. Ошибка должна произойти **после** записи. На второй попытке верни результат helper. Не реализуй цикл, sleep или собственный счётчик попыток в файле.

Так мы моделируем потерю подтверждения после побочного эффекта. Повтор должен найти один уже существующий выпуск, а успешные `validate_data` и `train_evaluate` остаются выполненными.

## Проверка настоящим SDK

```bash
export MLOPS_AIRFLOW_STAGE=2
docker compose -f labs/airflow/compose.yaml up -d --force-recreate
docker compose -f labs/airflow/compose.yaml exec -T -e MLOPS_RUN_SDK=1 airflow python -m pytest /course/modules/05-airflow/tasks/02-gate-retry/test_task.py -q
```

Тесты проверяют реальный граф и настройки retry, успешный выпуск и отказ при `gate_ratio=0.0` на синтетических данных с ненулевой ошибкой. Они исполняют учебные задачи через Airflow, не вызывая их Python-тела напрямую. Scheduler retry подтверждается отдельно ниже.

## Опыт через scheduler

Сначала проверь импорт и сними граф с паузы:

```bash
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags list-import-errors
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags unpause housing_pipeline
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags trigger --conf '{"fail_publish_once":true}' housing_pipeline
```

В UI найди созданный run. После первой ошибки publish появится возможность повтора, затем вторая попытка должна закончиться `success`. В папке releases остаётся один файл. Номер попытки обучения остаётся 1. Не очищай и не помечай задачи успешными вручную.

Можно автоматически создать изолированные запуски и проверить оба исхода. Команда выполняется на host в основной `.venv` при работающем и снятом с паузы DAG этапа 2:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 python scripts/run_task.py test 05-airflow/02-gate-retry -- -m writes
```

Тесты используют уникальные run IDs и каталоги `work/airflow-acceptance-*`. Один проверяет вторую попытку publish после записи, другой — отказ gate без выпуска. Они не запускают контейнеры, не очищают старые задачи и оставляют свои файлы для осмотра.

Для read-only проверки уже завершённого run укажи его ID. Здесь `pass` означает успешный gate и publish, `reject` — отклонение модели:

```bash
MLOPS_RUN_INTEGRATION=1 AIRFLOW_ACCEPTANCE_RUN_ID='свой-run-id' AIRFLOW_EXPECT_GATE=pass AIRFLOW_MIN_PUBLISH_ATTEMPTS=2 python scripts/run_task.py test 05-airflow/02-gate-retry -- -m 'integration and not writes'
```

## Завершение

Сохрани код и выпуск, они нужны третьему этапу. При перерыве используй `docker compose -f labs/airflow/compose.yaml down`. Учебный флаг не меняет качество модели и не входит в ключ обучения: он управляет только наблюдаемым сбоем публикации.

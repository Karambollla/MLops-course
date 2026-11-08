# Получить data interval из контекста Airflow

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Gate и retry](../02-gate-retry/README.md)

## Что предстоит сделать

Предыдущий граф можно запустить вручную, но запуск «сейчас» не описывает период данных. Теперь добавь ежедневное расписание и задачу, которая читает период из настоящего контекста Airflow. Итоговый граф: `prepare_interval → validate_data → train_evaluate → gate → publish`.

В [solution.py](solution.py) реализуй два компонента. Затем доработай `build_dag` первого задания только для `stage=3`. Нижние этапы сохраняют `schedule=None` и не загружают компонент интервала. [Назначение data interval](../../README.md#зачем-нужен-data-interval).

## Расписание

```python
def daily_schedule() -> CronDataIntervalTimetable:
    ...
```

Функция без аргументов возвращает настоящий `CronDataIntervalTimetable("0 0 * * *", timezone="UTC")`. Передай его в `schedule` декоратора `@dag` для третьего этапа. Фиксированный `start_date` остаётся первым января 2025 года, UTC. Сохрани `catchup=False`, `max_active_runs=1`.

Явный timetable нужен, чтобы получить интервалы данных, а не полагаться на подразумеваемую конфигурацию cron-расписаний. `catchup=False` не требует запустить все даты с начала расписания. Явный backfill позволяет отдельно обработать выбранный исторический диапазон.

## Задача prepare_interval

```python
def attach_interval_context() -> Any:
    ...
```

Функция вызывается без аргументов внутри фабрики DAG. Она создаёт `@task` с `task_id="prepare_interval"`, `retries=0` и возвращает TaskFlow-ссылку на её результат.

Внутри тела задачи вызови `get_current_context()`. Передай `context["data_interval_start"]` и `context["data_interval_end"]` готовой `interval_metadata(start, end)`. Это timezone-aware datetime, а не строки из параметров пользователя. Верни полученный словарь:

```json
{"data_interval_start":"2025-02-01T00:00:00+00:00","data_interval_end":"2025-02-02T00:00:00+00:00","partition":"2025-02-01"}
```

Пример описывает первое февраля. Интервал полуоткрытый: правая граница относится к следующему периоду. Helper нормализует границы в UTC и проверяет суточный интервал от полуночи до полуночи. Без timezone или при другой длительности возникает `ValueError`.

Не вызывай `get_current_context()` при разборе DAG. Контекст задачи существует только при её выполнении. Не вычисляй границы через `now()` и не копируй даты примера вместо обращения к SDK.

## Передать интервал в обучение

В `build_dag(stage=3)` создай компонент интервала и передай его TaskFlow-результат аргументом `interval` задачи `validate_data`. Она уже передаёт этот аргумент в `prepare_training`. Так появляется настоящая зависимость между задачами.

Helper включает интервал в устойчивый ключ, а после обучения сохраняет дополнительный `orchestration.json` рядом с четырьмя ML-артефактами. Файл содержит `path`, `run_key`, `model_version`, `interval`, `data_sha256`, `code_revision`, `seed`. Форматы `model.joblib`, `metrics.json`, `manifest.json` и `split.json` не меняются.

Два интервала дают два ключа даже на одном CSV. Retry публикации использует прежний XCom, а не новое время. В этом упражнении Housing CSV не меняется между датами: период фиксирует условия оркестрации, а не выдуманные ежедневные поступления данных.

## Проверка настоящим SDK

```bash
export MLOPS_AIRFLOW_STAGE=3
docker compose -f labs/airflow/compose.yaml up -d --force-recreate
docker compose -f labs/airflow/compose.yaml exec -T -e MLOPS_RUN_SDK=1 airflow python -m pytest /course/modules/05-airflow/tasks/03-failure-intervals/test_task.py -q
```

Проверяются настоящий timetable, зависимость `prepare_interval → validate_data` и выполнение для двух заданных моментов запуска в изолированной базе Airflow. Сохранённый интервал должен совпасть с XCom задачи, соседние периоды — дать разные каталоги. Это не проверка scheduler backfill, он запускается отдельно.

## Два интервала через scheduler

После успешного импорта сними DAG с паузы. Сначала посмотри план диапазона, затем создай backfill:

```bash
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags unpause housing_pipeline
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow backfill create --dag-id housing_pipeline --from-date 2025-02-01 --to-date 2025-02-02 --dry-run
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow backfill create --dag-id housing_pipeline --from-date 2025-02-01 --to-date 2025-02-02 --max-active-runs 1
docker compose -f labs/airflow/compose.yaml exec -T airflow airflow dags list-runs housing_pipeline
```

Границы команды задают диапазон logical dates, обе даты включены. Найди два выбранных запуска и сопоставь их data intervals с `orchestration.json`. Если выбранные даты уже успешно выполнялись, используй другой свободный соседний диапазон. Не заменяй этот опыт повторным вызовом чистой функции со строками дат.

Read-only тест принимает два завершённых run IDs и не создаёт новых запусков:

```bash
MLOPS_RUN_INTEGRATION=1 AIRFLOW_INTERVAL_RUN_IDS='["первый-run-id","второй-run-id"]' python scripts/run_task.py test 05-airflow/03-failure-intervals -- -m 'integration and not writes'
```

Чтобы отдельно проверить retry публикации и сохранность интервала на изолированном run:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 python scripts/run_task.py test 05-airflow/03-failure-intervals -- -m writes
```

Тест требует работающий и снятый с паузы DAG этапа 3. Он создаёт только свой run и файлы, наблюдает вторую попытку publish и единственный выпуск. Обычный запуск без флагов пропускает live-проверки.

## Завершение

Сохрани исходники и технические результаты. После остановки `docker compose -f labs/airflow/compose.yaml down` данные в `work/` и история в volume остаются. Для восстановления запуска нужны те же CSV, исходники, seed и интервал, а не совпавшее время повторного нажатия кнопки.

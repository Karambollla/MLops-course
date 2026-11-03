# Практика: Airflow: оркестрация ML-пайплайнов

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [DAG без подмены обучения](tasks/01-pipeline/README.md) | [Старт](tasks/01-pipeline/solution.py) · [Тесты функций](tasks/01-pipeline/test_task.py) | cpu |
| [Gate и повтор](tasks/02-gate-retry/README.md) | [Старт](tasks/02-gate-retry/solution.py) · [Тесты функций](tasks/02-gate-retry/test_task.py) | cpu |
| [Сбой и интервалы](tasks/03-failure-intervals/README.md) | [Старт](tasks/03-failure-intervals/solution.py) · [Тесты функций](tasks/03-failure-intervals/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=05-airflow/01-pipeline
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Функции проверяются на входах и результатах; проверки стенда включаются явно через MLOPS_RUN_INTEGRATION=1. Для руководств открой пример в README, автоматических проверок у них нет.

## Подготовка

```bash
docker compose -f labs/airflow/compose.yaml up -d --build
docker compose -f labs/airflow/compose.yaml logs --tail=80
```

UI: `http://localhost:8080`. Учётные данные standalone появляются в логах и файле конфигурации auth manager внутри volume; это отдельный локальный стенд. Не используй инструкцию `airflow users create` из старых курсов без проверки Airflow 3.

## Завершение

Останови Airflow перед Kubernetes: `docker compose -f labs/airflow/compose.yaml down`. Данные остаются в `work/` и named volume. Удаление volume сбрасывает историю DAG.

## Обязательные признаки настоящего исполнения

Тесты чистых функций и fake subprocess не заменяют Airflow. В теме 01 есть
read-only opt-in загрузка DAG настоящим Airflow SDK внутри уже работающего
контейнера: `MLOPS_RUN_INTEGRATION=1 python -m pytest
modules/05-airflow/tasks/01-pipeline -m integration -q`. Она проверяет только
импорт/граф. Тела gate/publish и interval wiring остаются student TODO.

Практика завершена после настоящего запуска DAG, проверки отдельных task
instances и XCom, существующих model/metrics/release, retry только упавшего
publish без дубликата и двух суточных прошлых UTC интервалов. Конкретные критерии
и команды — в README тем 01–03. Записывающие автоматические проверки требуют
`MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1` и markers `integration`, `writes`;
они не должны самостоятельно поднимать стенд или массовый backfill.

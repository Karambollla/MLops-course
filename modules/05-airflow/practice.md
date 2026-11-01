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

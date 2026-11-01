# Практика: Airflow: оркестрация ML-пайплайнов

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [DAG без подмены обучения](tasks/01-pipeline/README.md) | [Заготовка](tasks/01-pipeline/solution.py) · [тесты](tasks/01-pipeline/test_task.py) | cpu |
| [Gate и повтор](tasks/02-gate-retry/README.md) | [Заготовка](tasks/02-gate-retry/solution.py) · [тесты](tasks/02-gate-retry/test_task.py) | cpu |
| [Сбой и интервалы](tasks/03-failure-intervals/README.md) | [Заготовка](tasks/03-failure-intervals/solution.py) · [тесты](tasks/03-failure-intervals/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=05-airflow/01-pipeline
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

```bash
docker compose -f labs/airflow/compose.yaml up -d --build
docker compose -f labs/airflow/compose.yaml logs --tail=80
```

UI: `http://localhost:8080`. Учётные данные standalone появляются в логах и файле конфигурации auth manager внутри volume; это отдельный локальный стенд. Не используй инструкцию `airflow users create` из старых курсов без проверки Airflow 3.

## Завершение

Останови Airflow перед Kubernetes: `docker compose -f labs/airflow/compose.yaml down`. Данные остаются в `work/` и named volume. Удаление volume сбрасывает историю DAG.

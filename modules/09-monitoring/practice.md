# Практика: Prometheus, Grafana и качество модели

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Нагрузка и dashboard](tasks/01-load-dashboard/README.md) | [Заготовка](tasks/01-load-dashboard/solution.py) · [тесты](tasks/01-load-dashboard/test_task.py) | cpu |
| [Отказ](tasks/02-outage/README.md) | [Заготовка](tasks/02-outage/report.json) · [тесты](tasks/02-outage/test_task.py) | cpu |
| [Качество и drift](tasks/03-quality-drift/README.md) | [Заготовка](tasks/03-quality-drift/solution.py) · [тесты](tasks/03-quality-drift/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=09-monitoring/01-load-dashboard
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

Останови API другого Compose-стенда и kind при недостатке ресурсов.

```bash
docker compose -f labs/monitoring/compose.yaml up -d --build
```

Prometheus: 9090; Grafana: 3000, локальный вход student / local-course-only. Dashboard Housing course и datasource создаются автоматически. Без модели API жив, но predict даёт 503.

## Завершение

`docker compose -f labs/monitoring/compose.yaml down`. Перед удалением volume выгрузи свой dashboard JSON и отчёт.

# Практика: ClearML: задачи, артефакты и агенты

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Основной путь: Mac CPU](tasks/01-offline/README.md) | [Заготовка](tasks/01-offline/solution.py) · [тесты](tasks/01-offline/test_task.py) | cpu |
| [Дополнительный путь: Server и Agent](tasks/02-agent/README.md) | [Заготовка](tasks/02-agent/report.json) · [тесты](tasks/02-agent/test_task.py) | linux-x86_64 |
| [Сравнение и отказ](tasks/03-comparison-failure/README.md) | [Заготовка](tasks/03-comparison-failure/report.json) · [тесты](tasks/03-comparison-failure/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=06-clearml/01-offline
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Завершение

Agent останови Ctrl+C. Server: `docker compose -f labs/clearml/compose.yaml down`. Сначала экспортируй отчёт, затем при необходимости `down -v`. Offline-сессии остаются в cache ClearML; путь показывает SDK.

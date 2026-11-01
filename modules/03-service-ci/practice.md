# Практика: ML-сервис, Docker и CI

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Контракт](tasks/01-api-contract/README.md) | [Заготовка](tasks/01-api-contract/solution.py) · [тесты](tasks/01-api-contract/test_task.py) | cpu |
| [Образ](tasks/02-container/README.md) | [Заготовка](tasks/02-container/evidence.json) · [тесты](tasks/02-container/test_task.py) | cpu |
| [CI](tasks/03-ci/README.md) | [Заготовка](tasks/03-ci/ci-runs.json) · [тесты](tasks/03-ci/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=03-service-ci/01-api-contract
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Завершение

Останови Uvicorn через Ctrl+C. Для контейнеров: `docker compose -f labs/housing/compose.yaml down`. Артефакты в `work/artifacts` остаются.

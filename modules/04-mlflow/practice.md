# Практика: MLflow: эксперименты и реестр моделей

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Три запуска](tasks/01-experiments/README.md) | [Заготовка](tasks/01-experiments/solution.py) · [тесты](tasks/01-experiments/test_task.py) | cpu |
| [Registry](tasks/02-registry/README.md) | [Заготовка](tasks/02-registry/solution.py) · [тесты](tasks/02-registry/test_task.py) | cpu |
| [Отказ](tasks/03-outage/README.md) | [Заготовка](tasks/03-outage/solution.py) · [тесты](tasks/03-outage/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=04-mlflow/01-experiments
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

```bash
docker compose -f labs/mlflow/compose.yaml up -d --build
curl -I http://localhost:5001
```

Порт на ноутбуке — 5001, внутри контейнера — 5000. Это позволяет избежать конфликта с системным сервисом macOS на 5000.

Для SDK используй отдельное окружение с requirements из `labs/mlflow/requirements.txt`; оно включает базовые зависимости проекта. Установи housing в него через `pip install --no-deps -e labs/housing`.

## Завершение

`docker compose -f labs/mlflow/compose.yaml down` сохраняет volume. Перед `down -v` экспортируй IDs, отчёт и нужные артефакты.

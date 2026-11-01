# Практика: MLflow: эксперименты и реестр моделей

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Три запуска](tasks/01-experiments/README.md) | [Старт](tasks/01-experiments/solution.py) · [Тесты функций](tasks/01-experiments/test_task.py) | cpu |
| [Registry](tasks/02-registry/README.md) | [Старт](tasks/02-registry/solution.py) · [Тесты функций](tasks/02-registry/test_task.py) | cpu |
| [Отказ](tasks/03-outage/README.md) | [Старт](tasks/03-outage/solution.py) · [Тесты функций](tasks/03-outage/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=04-mlflow/01-experiments
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Функции проверяются на входах и результатах; проверки стенда включаются явно через MLOPS_RUN_INTEGRATION=1. Для руководств открой пример в README, автоматических проверок у них нет.

## Подготовка

```bash
docker compose -f labs/mlflow/compose.yaml up -d --build
curl -I http://localhost:5001
```

Порт на ноутбуке — 5001, внутри контейнера — 5000. Это позволяет избежать конфликта с системным сервисом macOS на 5000.

Для SDK используй отдельное окружение с requirements из `labs/mlflow/requirements.txt`; оно включает базовые зависимости проекта. Установи housing в него через `pip install --no-deps -e labs/housing`.

## Завершение

`docker compose -f labs/mlflow/compose.yaml down` сохраняет volume. Удаление volume не требуется; перед его намеренным удалением сохрани идентификаторы запусков, release manifest и нужные артефакты.

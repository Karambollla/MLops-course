# Практика: ML и оценка моделей

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Baseline](tasks/01-baseline/README.md) | [Заготовка](tasks/01-baseline/solution.py) · [тесты](tasks/01-baseline/test_task.py) | cpu |
| [Кандидат](tasks/02-candidate/README.md) | [Заготовка](tasks/02-candidate/solution.py) · [тесты](tasks/02-candidate/test_task.py) | cpu |
| [Анализ ошибок](tasks/03-error-analysis/README.md) | [Заготовка](tasks/03-error-analysis/solution.py) · [тесты](tasks/03-error-analysis/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=01-ml/01-baseline
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

```bash
python -m housing.data --output work/housing.csv
```

Заготовки метрик и обучения находятся в `tasks/01-baseline/` и `tasks/02-candidate/`. Команда `python -m housing.train` вызывает этот учебный код через адаптер. Данные загружаются один раз, затем практика работает локально.

## Завершение

Сохрани артефакты для модулей 02–05. Docker-стенд отсутствует; CSV и split не удаляй.

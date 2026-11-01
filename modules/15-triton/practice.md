# Практика: Triton Inference Server и перенос модели

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Экспорт и ONNX parity](tasks/01-onnx/README.md) | [Заготовка](tasks/01-onnx/solution.py) · [тесты](tasks/01-onnx/test_task.py) | cpu |
| [Triton: запрос и готовность модели](tasks/02-server/README.md) | [Заготовка](tasks/02-server/solution.py) · [тесты](tasks/02-server/test_task.py) | linux-x86_64 |
| [Сравнение inference latency](tasks/03-benchmark/README.md) | [Заготовка](tasks/03-benchmark/solution.py) · [тесты](tasks/03-benchmark/test_task.py) | linux-x86_64 |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=15-triton/01-onnx
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Завершение

Triton: `docker compose -f labs/triton/compose.yaml down`. Сохрани ONNX вне Git вместе с hash/manifest. Для основного Mac-пути деактивируй отдельный venv.

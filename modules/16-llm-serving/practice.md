# Практика: vLLM, SGLang и TensorRT-LLM

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Память, SSE и корпус запросов](tasks/01-memory-contract/README.md) | [Заготовка](tasks/01-memory-contract/solution.py) · [тесты](tasks/01-memory-contract/test_task.py) | cpu |
| [vLLM и SGLang: измерения](tasks/02-engines/README.md) | [Заготовка](tasks/02-engines/solution.py) · [тесты](tasks/02-engines/test_task.py) | nvidia |
| [TensorRT-LLM: собственный engine](tasks/03-tensorrt/README.md) | [Заготовка](tasks/03-tensorrt/engine-report.json) · [тесты](tasks/03-tensorrt/test_task.py) | nvidia |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=16-llm-serving/01-memory-contract
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Завершение

Останови активный Compose-стенд. Cache весов сохраняется в named volume; удаление через down -v потребует повторного скачивания. Не запускай два сервера на одном порту или одной малой GPU одновременно.

# Практика: архитектура LLM-serving и локальные расчёты

[Теория](README.md) · [Подсказки](hints.md)

## Темы

| Тема | Реализация и проверка | Среда |
|---|---|---|
| [Память, KV cache и подготовленные SSE](tasks/01-memory-contract/README.md) | solution.py и прямые тесты формул/парсинга | CPU |
| [TTFT и TPOT](tasks/02-engines/README.md) | solution.py и тесты по временным событиям | CPU |
| [TensorRT-LLM и backend](tasks/03-tensorrt/README.md) | Справочное руководство | Чтение материалов |

## Запуск

```bash
make task TASK=16-llm-serving/01-memory-contract
make task TASK=16-llm-serving/02-engines
```

Зависимости — основное окружение SETUP. Для этих проверок не требуются веса модели, GPU и LLM API. Незавершённые функции дают `NotImplementedError`.

## Пропущенные сценарии

Генерация и streaming через vLLM/SGLang API, нагрузочные бенчмарки этих endpoints и генерация через TensorRT-LLM/Triton backend пропущены. Они не имитируются. Конфигурации в `labs/llm/` остаются справочными примерами, а прохождение локальных тестов не подтверждает работу engines.

В подготовленных событиях изучается формат и арифметика измерений, а не производительность модели. Публиковать их как реальные результаты benchmark нельзя.

# TensorRT-LLM: checkpoint, engine и Triton backend

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## Что изучается

TensorRT-LLM может требовать преобразования checkpoint и сборки engine под модель, dtype, shapes и GPU. Triton backend затем загружает engine; ensemble может включать токенизацию и обработку результата. Открытый shell в контейнере не подтверждает ни сборку, ни inference.

Это справочное руководство. API-зависимые сценарии генерации TensorRT-LLM и соответствующего Triton backend пропущены. Обращения к LLM endpoints и их имитация не входят в практику; проходить GPU-лабораторную ради этого раздела не нужно.

## Путь данных и артефактов

| Этап | Вход | Результат |
|---|---|---|
| Checkpoint | Model ID, immutable revision и tokenizer | Сохранённые веса и конфигурация архитектуры |
| Conversion | Совместимый checkpoint и поддерживаемый путь релиза | Представление весов для builder |
| Build | Веса, dtype, shapes/лимиты и GPU | Engine и метаданные сборки |
| Repository | Engine, backend config и tensor names | Структура загрузки Triton |
| Serving | Repository и совместимый runtime | Обработка запросов; в этом курсе не выполняется |

Изучи [архивное руководство backend 25.06](https://docs.nvidia.com/deeplearning/triton-inference-server/archives/triton-inference-server-2560/user-guide/docs/tensorrtllm_backend/README.html): requirements, conversion/build, model repository и связь preprocessing с engine. Сопоставляй примеры со встроенными версиями выбранного образа. Тег 24.07 внутри иллюстрации не делает engine совместимым с 25.06. Поддержку Qwen нельзя предполагать только из-за её использования в другом runtime.

Файл `labs/llm/tensorrt-llm.sh` служит примером запуска контейнера с GPU. Он не собирает engine автоматически, а результаты без bind mount исчезают вместе с временным контейнером. Чтение этого файла не считается runtime-опытом.

## Границы сравнения

Разные модели, tokenizer, длины запросов или cache делают сравнение engines несопоставимым. Engine может зависеть от GPU и релиза TensorRT. Не указывай скорость или поддержку hardware по результату чтения конфигурации. Подробнее — [TensorRT-LLM и Triton](../../README.md#tensorrt-llm-и-triton).

Обязательного отчёта и автоматических тестов в руководстве нет. Локальные расчёты памяти и streaming-метрик выполняются в предыдущих темах; они не подтверждают генерацию через API.

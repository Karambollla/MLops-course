# 16. vLLM, SGLang и TensorRT-LLM

[Программа](../../README.md) · [Практика](practice.md) · [Подсказки](hints.md)

## Цель и границы

Понимать устройство LLM-serving, оценивать потребность в памяти и проводить честное сравнение движков. Нужны HTTP, основы матричных вычислений и модуль 15. Основной Mac-маршрут — расчёты, контракты, чтение документации и анализ. NVIDIA-запуск дополнительный; CPU-разбор не даёт права заявлять практику GPU-serving.

## Prefill, decode и метрики

Prefill обрабатывает входной prompt и строит состояния attention. Decode генерирует следующие tokens последовательно. Длинный prompt увеличивает работу prefill, длинный ответ — число decode steps. Одинаковое количество запросов в секунду не характеризует нагрузку, если длины сильно различаются.

TTFT — время от отправки запроса до первого полезного token. End-to-end latency — до завершения ответа. Inter-token latency и TPOT описывают генерацию после первого token, но разные инструменты могут использовать разные точные определения. При сохранении измерений указывай определение каждой метрики и единицу измерения. Первый network chunk не всегда содержит полезный token: streaming-ответ может сначала передать служебные поля.

Throughput можно считать в requests/s, output tokens/s или total tokens/s. Всегда подписывай знаменатель и что включено в число tokens. Одна удачная генерация не является нагрузочным тестом.

## Память и KV cache

Веса занимают примерно число параметров × байт на параметр: 0,5 млрд параметров в FP16 — около 1 млрд байт до накладных расходов. KV cache растёт с длиной контекста и числом одновременно обслуживаемых последовательностей. Упрощённая оценка байтов: `2 × layers × kv_heads × head_dim × cached_tokens × bytes_per_element`. Для GQA число kv_heads может быть меньше числа attention heads.

Эта формула не учитывает все временные buffers, allocator overhead, quantization metadata и особенности движка. Поэтому нельзя заполнить VRAM весами «до последнего мегабайта» и ожидать большой batch. Выбранные context length и concurrency надо проверять фактически.

## Почему специализированные движки

Continuous batching позволяет добавлять новые запросы по мере завершения старых. Paged KV storage уменьшает проблемы фрагментации и управления cache. Prefix caching переиспользует одинаковый префикс, но его полезность зависит от нагрузки. Эти механизмы не отменяют очереди, timeouts и ограничение числа одновременных запросов.

vLLM предоставляет serving с совместимыми API и специализированным планированием. SGLang также предлагает runtime для LLM с оптимизациями исполнения и cache. Сравнивать их нужно на закреплённых версиях, модели и workload, а не по универсальному рейтингу. Поддержка hardware и CLI меняется: инструкции latest могут не подходить к старому image.

## Triton и TensorRT-LLM

TensorRT-LLM — стек оптимизации/исполнения LLM для NVIDIA. Triton может обслуживать его через соответствующий backend. Это не четвёртый независимый HTTP-wrapper, идентичный vLLM. Для некоторых путей нужны conversion/build и engine, привязанный к релизу и hardware; текущие API могут предоставлять другие способы загрузки. В этой лабораторной строго используется guide релиза 25.06, а не команды нового 25.12.

## Протокол сравнения

Зафиксируй model ID и revision, tokenizer, dtype/quantization, context limit, input/output tokens, temperature, seed если поддерживается, concurrency, warmup, число измерений и ошибки. Для SGLang и vLLM используй один prompt corpus. Температура 0 не гарантирует побитово одинаковый текст между реализациями; производительность и качество ответа проверяются отдельно.

OpenAI-compatible endpoint не гарантирует поддержку всех параметров и одинаковые ошибки. Проверь streaming, отмену клиентом, oversized context и недоступную модель. Следи, чтобы запрос с max_tokens=64 действительно был сопоставим по числу сгенерированных tokens.

## Материалы

- [vLLM documentation](https://docs.vllm.ai/en/v0.10.2/) — версия лабораторной: serving, metrics и installation.
- [SGLang repository](https://github.com/sgl-project/sglang/tree/v0.4.10.post2) — README и docs именно выбранного тега; latest CLI может отличаться.
- [TensorRT-LLM backend 25.06](https://docs.nvidia.com/deeplearning/triton-inference-server/archives/triton-inference-server-2560/user-guide/docs/tensorrtllm_backend/README.html) — conversion, engine и model repository релиза 25.06.
- [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) — архитектура, лицензия, tokenizer и ограничения маленькой модели.

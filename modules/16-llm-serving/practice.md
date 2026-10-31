# Практика: vLLM, SGLang и TensorRT-LLM

[Теория](README.md) · [Подсказки](hints.md)

## Обязательная часть: Mac без NVIDIA

1. Создай `work/llm-plan.md`: оцени веса FP16 для 0,5B и 7B, затем KV cache при layers=24, kv_heads=8, head_dim=64, context=2048 и FP16 для concurrency 1 и 8.
2. Изучи `labs/llm/request.json` и опиши обработку SSE: служебные chunks, первый непустой content, завершение, ошибка, отмена.
3. Подготовь корпус из 20 prompts с разными длинами и шаблон результатов benchmark.csv. Укажи, какие параметры нельзя сравнивать без GPU.

Для этих заданий не нужны платные API и фиктивный сервер.

## Дополнительная часть: Linux NVIDIA

Проверь nvidia-smi, Docker GPU runtime и compatibility выбранных images. Запускай последовательно:

```bash
docker compose -f labs/llm/vllm.compose.yaml up -d
curl -sS http://localhost:8000/v1/models
curl -N http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' --data-binary @labs/llm/request.json
```

После сохранения результатов останови vLLM, затем повтори для `labs/llm/sglang.compose.yaml`. Первый запуск скачивает публичную маленькую модель; проверь её model card и доступность. Веса фиксируй revision при подготовке окончательного benchmark.

Напиши клиент измерений: TTFT по первому непустому content, end-to-end, output tokens, ошибки. Минимум 20 warmup и 100 измеряемых запросов при concurrency 1 и 4. Сохраняй отдельные строки по запросам, а не только среднее.

## TensorRT-LLM

Скрипт `bash labs/llm/tensorrt-llm.sh` открывает контейнер закреплённого backend, но не запускает готовую модель. По архивной документации 25.06 выбери поддерживаемую модель и выполни preparation/build/configuration для своего GPU. Маленькая модель предыдущего упражнения может не поддерживаться этим релизом. Запиши точные команды, engine metadata и успешный inference. Не сравнивай разные модели как доказательство скорости движков.

## Критерии готовности

- [ ] Объяснены prefill/decode, KV cache, batching и определения метрик.
- [ ] Расчёт памяти содержит накладные расходы как ограничение оценки.
- [ ] Для GPU-части есть реальные per-request данные либо честная отметка «не выполнялось».
- [ ] TensorRT-LLM связан с Triton backend и release-specific совместимостью.

## Завершение

Останови активный Compose-стенд. Cache весов сохраняется в named volume; удаление через down -v потребует повторного скачивания. Не запускай два сервера на одном порту или одной малой GPU одновременно.

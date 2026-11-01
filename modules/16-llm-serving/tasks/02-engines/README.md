# vLLM и SGLang: измерения

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## С чего начать

Реализуй `request_metrics(started, events, ended, output_tokens)`: events — список {time, content}; времена в секундах monotonic, служебные/пустые content не являются первым token. Результат ttft_ms, total_ms, output_tokens, tpot_ms; TPOT=(total-TTFT)/(tokens-1), для одного token — None. Отсутствие полезного content, несогласованные времена и неположительное число tokens — ValueError. Это unit-проверка определения метрик, а не GPU-бенчмарк. Для реального сравнения отдельно заполни benchmark.json, не меняя модель/revision/корпус между engines.

Подготовь [основное окружение](../../../../SETUP.md). Все команды ниже выполняются из корня курса. Платформа задания: **nvidia**. Функции и ожидаемые результаты описаны также в `test_task.py`; тесты используют небольшие фиксированные данные.

## Исходное задание

Проверь nvidia-smi, Docker GPU runtime и compatibility выбранных images. Запускай последовательно:

```bash
docker compose -f labs/llm/vllm.compose.yaml up -d
curl -sS http://localhost:8000/v1/models
curl -N http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' --data-binary @labs/llm/request.json
```

После сохранения результатов останови vLLM, затем повтори для `labs/llm/sglang.compose.yaml`. Первый запуск скачивает публичную маленькую модель; проверь её model card и доступность. Веса фиксируй revision при подготовке окончательного benchmark.

Напиши клиент измерений: TTFT по первому непустому content, end-to-end, output tokens, ошибки. Минимум 20 warmup и 100 измеряемых запросов при concurrency 1 и 4. Сохраняй отдельные строки по запросам, а не только среднее.

## Проверка

```bash
make task TASK=16-llm-serving/02-engines
```

У этой задачи проверяются функции: запускай их тестами, отдельного CLI нет.

До реализации функции ожидается `NotImplementedError`; для отчётов — ошибка незаполненного поля. Исправляй заготовку или собственный результат, сохраняя ожидаемое поведение тестов. Офлайн-тест не подтверждает действия на внешнем стенде: проверки, требующие работающего сервиса, включаются явно через `MLOPS_RUN_INTEGRATION=1`.

## Критерии и завершение

На Mac можно выполнить unit-часть, выбрав тесты `-k "not submitted_gpu"`; полный зачёт этой дополнительной задачи требует собственных GPU-измерений. Автоматическая схема не подтверждает происхождение цифр: покажи nvidia-smi, версии, исходные 100 строк на concurrency, tokenizer и контроль ошибок. Останови сервер после экспорта результатов.

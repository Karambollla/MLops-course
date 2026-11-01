# vLLM и SGLang: измерения

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## Зачем измерять первый полезный content

Streaming может передать role сразу, а текст — значительно позже. Если поставить TTFT по первой сетевой активности, сравнение engines будет неверным. Определения и численный пример находятся в [TTFT/TPOT](../../README.md#ttft-tpot-и-throughput), параметры стенда — в [разборе Compose](../../README.md#что-означают-параметры-compose).

Уже предоставлены `solution.py`, пустой массив `benchmark.json` для исходных строк, корпус prompts первого задания и два Compose в `labs/llm/`. Функцию метрик можно проверить на локальном CPU в [основном окружении](../../../../SETUP.md). Реальный benchmark требует отдельного совместимого Linux/NVIDIA стенда; CPU-проверка функции его не заменяет.

## Контракт метрики запроса

Реализуй `request_metrics(started,events,ended,output_tokens) -> dict`. Времена — секунды одного monotonic clock, events — упорядоченные `{time,content}` внутри интервала started..ended. Результат содержит `ttft_ms`, `total_ms`, `output_tokens`, `tpot_ms`. Первый полезный event имеет непустой content; служебное пустое поле не подходит.

TTFT — интервал от started до первого content; total — started..ended; TPOT=`(total_ms-ttft_ms)/(output_tokens-1)`. При одном token TPOT=None. Нет полезного content, времена несогласованы или output_tokens неположительно — ValueError. Не подменяй число output tokens количеством событий.

Для started=0.9, пустого content в 1.0, текста в 1.15, ended=1.5 и output_tokens=4 ожидаются TTFT=250 ms, total=600 ms, TPOT≈116.67 ms. Это пример определения, а не скорость Qwen.

## Последовательный запуск engines

Перед запуском проверь `nvidia-smi`, Docker GPU runtime, доступную VRAM и совместимость pinned images/модели/драйвера. Из корня курса:

```bash
docker compose -f labs/llm/vllm.compose.yaml up -d
curl --fail http://127.0.0.1:8000/v1/models
curl -N --fail http://127.0.0.1:8000/v1/chat/completions -H 'Content-Type: application/json' --data-binary @labs/llm/request.json
```

Первый запуск скачивает публичную маленькую модель. В `/v1/models` ожидается имя `course-llm`; в streaming — непустой content и завершение `[DONE]`. Это проверяет запрос, но ещё не нагрузку. Для итогового benchmark закрепи одну immutable model revision/tokenizer для обоих engines; исходные Compose задают model ID без revision.

Подготовь клиент, сохраняющий timestamps, content events, фактическое число output tokens и ошибки. Выполни минимум 20 warmup и 100 измеряемых запросов при concurrency 1 и 4. Сохраняй по строке на запрос: например engine, concurrency, request_id, ttft_ms, total_ms, output_tokens, status, а рядом — hardware, image digest, model revision и параметры генерации. Общая длительность серии нужна для throughput.

Останови vLLM перед запуском SGLang:

```bash
docker compose -f labs/llm/vllm.compose.yaml down
docker compose -f labs/llm/sglang.compose.yaml up -d
```

Повтори тот же запрос и протокол. Не меняй prompts, длины, dtype или cache-условия ради лучшего результата. max_tokens — максимум, не гарантированная длина. Ошибки и отменённые запросы сохраняй отдельно от успешных генераций. [Протокол сравнения](../../README.md#протокол-честного-сравнения) объясняет, какие условия делают числа сопоставимыми.

## Проверка и завершение

```bash
make task TASK=16-llm-serving/02-engines
```

Тесты проверяют функцию метрик и доступны без GPU; CLI нет. Они не отправляют реальные запросы. Без NVIDIA можно изучить команды и выполнить расчёты, сохраняя границу между теорией и запуском. Универсального ожидаемого RPS нет.

После сохранения исходных измерений останови `docker compose -f labs/llm/sglang.compose.yaml down`. Cache весов остаётся в volume; удаление через `down -v` потребует скачивания заново. `benchmark.json` — место для технических данных, не обязательный текстовый отчёт.

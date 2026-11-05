# Измерить latency настоящим клиентом

[Модуль и подготовка](../../README.md#подготовка-к-заданиям) · [Все задания модуля](../../README.md#задания) · [Окружение курса](../../../../SETUP.md)

## Что измеряется

Сначала проверь численную корректность модели [заданием 02](../02-server/README.md). Здесь один и тот же batch отправляется последовательно: это baseline с concurrency=1. Чистая функция summary проверяется без сервера, настоящий benchmark использует твой SDK-клиент.

## Функции и их входы

### `latency_summary(rows: list[dict], elapsed_seconds: float, min_requests: int = 200) -> dict`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `rows` | `list[dict]` | Измерения с `latency_ms` и `status`. Не строки исходных признаков | Поле `rows` результата `benchmark` | `[{"latency_ms":10,"status":200}, ...]` |
| `elapsed_seconds` | `float` | Положительное конечное стенное время всей серии в секундах | Отдельные отметки perf_counter до и после измеряемой серии | `1.0` |
| `min_requests` | `int` | Минимум строк, требуемый для summary | 200 для baseline, меньший порог только в коротком тесте | `200` |

Верни `p50_ms`, `p95_ms`, `throughput_rps`, `error_ratio`. Процентили линейные по всем строкам, включая ошибочные. Throughput равен числу всех rows, делённому на elapsed_seconds. Error ratio — доля status>=400. Для latency 10/20/30 ms за одну секунду с одной ошибкой результат: p50=20, p95=29, throughput=3, error_ratio=1/3 при min_requests=3.

Недостаточное число rows, отрицательная/неконечная latency или неположительное/неконечное elapsed вызывают `ValueError`. Нулевая latency допустима. Не подменяй elapsed суммой задержек запросов.

### `benchmark(client, rows: list[dict], feature_order: list[str], requests=200, warmup=5, model_name="housing", output_names=("variable",)) -> dict`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | HTTP SDK-клиент Triton | Клиент уже доступной модели | `create_client` из задания 02 | Уже открытый клиент |
| `rows` | `list[dict]` | Batch входных признаков. Здесь это данные модели, а не измерения | JSON-список из CLI `--rows` | Одна housing-строка без target |
| `feature_order` | `list[str]` | Порядок признаков для каждого запроса | `housing.features.FEATURES` | `list(FEATURES)` |
| `requests` | `int` | Положительное число измеряемых вызовов, без `bool` | CLI `--requests` | `200` |
| `warmup` | `int` | Неотрицательное число прогревочных вызовов, без `bool` | CLI `--warmup` | `5` |
| `model_name` | `str` | Имя модели для student infer | Repository Triton | `"housing"` |
| `output_names` | Последовательность `str` | Имена outputs для student infer | Metadata модели | `("variable",)` |

Вызови `load_task("15-triton/02-server").infer` сначала warmup раз, затем requests раз с теми же входами. Используй `perf_counter` для каждого измеряемого запроса и отдельно для всей измеряемой серии. Warmup не входит ни в rows, ни в elapsed. Ошибка warmup прекращает эксперимент.

Форма результата: `{"rows":[{"latency_ms":1.2,"status":200}],"elapsed_seconds":0.002}`. Числа иллюстрируют структуру, а не скорость сервера. Успешный вызов получает status=200. Ошибка измеряемого вызова записывается как status=500 с его фактической длительностью. Здесь 500 — маркер ошибки клиента, а не восстановленный HTTP-код SDK. Не сохраняй тело ответа или текст исключения. Неверные requests/warmup дают `ValueError` до сети.

## Готовый CLI

| Аргумент или переменная | Формат и назначение | По умолчанию |
|---|---|---|
| `--rows` | Обязательный путь к JSON-списку housing-строк | Нет |
| `--url` / `TRITON_URL` | Адрес того же HTTP-сервера, что в задании 02 | `http://127.0.0.1:8000` |
| `--requests` | Число измеряемых вызовов. CLI требует не меньше 200 | `200` |
| `--warmup` | Число вызовов до начала измеряемой серии | `5` |
| `--output` | Обязательный путь JSON с rows, elapsed_seconds и summary | Нет |
| `MLOPS_RUN_INTEGRATION` | `1` включает короткий live-тест, не запускает сервер | Без флага тест пропущен |

Функция допускает requests=3 для короткой проверки. CLI с таким числом завершится ошибкой аргументов, поскольку полноценный baseline требует >=200. [benchmark.csv](benchmark.csv) — необязательный шаблон с заголовками `request_id`, `engine`, `hardware`, `batch`, `concurrency`, `latency_ms`, `status`. Автоматический CLI сохраняет JSON, CSV за тебя не заполняет.

## Запуск проверки и baseline

```bash
make task TASK=15-triton/03-benchmark
python scripts/run_task.py run 15-triton/03-benchmark --rows work/triton/rows.json --requests 200 --warmup 5 --output work/triton/benchmark.json
MLOPS_RUN_INTEGRATION=1 make task TASK=15-triton/03-benchmark
```

CLI создаёт настоящий HTTP SDK client с `TRITON_URL`, вызывает benchmark, применяет latency_summary **к возвращённым сырым замерам** и сохраняет rows/elapsed_seconds/summary в указанный JSON. Выводит summary. Используй существующий JSON-список housing строк. Зависимости и платформа — как в задании 02. Fast tests подменяют лишь infer/часы для проверки warmup/ошибок/границ. Live probe делает короткую реальную серию твоим клиентом. Только полный CLI-прогон >=200 запросов является baseline benchmark, короткий live probe проверяет взаимодействие.

Сравнивай FastAPI/Triton на одной модели, данных, batch и hardware. Для concurrency=4 нужен отдельный опыт с независимыми клиентами на worker либо согласованным async SDK: `InferenceServerClient` не thread safe, разделять один экземпляр между потоками нельзя. Сохрани сырые CSV/JSON, wall time, версии/ресурсы. Файл benchmark.csv содержит только заголовок. Рост throughput при росте p95 требует оценки компромисса, метрики 8002 не заменяют клиентский интервал. Без совместимого Triton не объявляй тесты с doubles измерением сервера.

Останови `docker compose -f labs/triton/compose.yaml down` после опыта.

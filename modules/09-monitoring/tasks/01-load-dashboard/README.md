# Нагрузка и dashboard

## Зачем сравнивать клиент и dashboard

Увеличение concurrency, числа одновременно выполняемых запросов, может повысить throughput и одновременно ухудшить хвост задержек. Нужно сохранить измерения нагрузки и понять, какие из них Prometheus оценивает по другому временному окну. График без реальных predict-запросов этого не показывает.

Исходное состояние — готовая HTTP-инструментация API и Compose с Prometheus/Grafana. Для успешного predict нужен твой bundle в `work/artifacts`; в `solution.py` не реализован расчёт итогов. Связь компонентов смотри в [пути метрики](../../README.md#путь-запроса-и-путь-метрики), формулы — в [счётчиках и длительности](../../README.md#счётчики-длительность-и-запросы).

## Контракт функции и измерений

`run` содержит `concurrency`, `requests`, `seconds`, `status_counts` со строковыми HTTP-кодами и `p95_seconds`. Результат имеет только `rps`, `error_ratio`, `p95_seconds`. Например, 20 запросов за 4 секунды, из них два 503 и p95=.2, дают 5 RPS, .1 доли 5xx и .2 секунды p95. Функция обобщает уже измеренную p95, не восстанавливает её по счётчикам статусов. Ты реализуешь расчёт и проверки входа, затем редактируешь панели в `dashboard.json`; фиксированный scenario не является замером работающего API.

## Реальные измерения

Дополнительно реализуй `measure_load(url, payload, requests=200, concurrency=1) -> dict`: выполни указанное число настоящих POST-запросов к housing `/predict`, измерь длительность каждого через `perf_counter` и общую длительность серии. Верни `concurrency`, `requests`, `seconds`, `status_counts` со строковыми кодами, `p95_seconds` как 95-й процентиль исходных длительностей с линейной интерполяцией и сами `durations_seconds`.

Не включай warmup или `/metrics` в эту серию. HTTP 4xx/5xx сохраняй как ответы с соответствующим статусом, сетевую ошибку не выдавай за HTTP 200. Транспорт реализуется тобой с подготовленными HTTP-импортами. Передавай результат в `summarize_run`, сохраняя исходные длительности отдельно от сводки.

После подготовки API с моделью, Prometheus и Grafana:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 HOUSING_URL=http://127.0.0.1:8000 PROMETHEUS_URL=http://127.0.0.1:9090 python scripts/run_task.py test 09-monitoring/01-load-dashboard -- -m writes
```

Тест вызывает твою `measure_load`, сверяет 24 ответа и p95, затем ожидает увеличение `http_requests_total{route="/predict"}` в настоящем Prometheus. Он создаёт реальный трафик, поэтому требует дополнительного флага. Не выполняй его одновременно с другими нагрузочными опытами. В Grafana сверяй datasource Prometheus и панели своего dashboard; тест не заменяет настройку запросов и оповещений.

## Реализация и запуск

Реализуй `summarize_run(run)` в `solution.py`. Верни `rps=requests/seconds`, `error_ratio=5xx/requests`, `p95_seconds` без изменения. При нулевом трафике: rps=0, остальные два поля None. Требуй seconds>0, concurrency>=1, неотрицательные целые counts с суммой requests и p95>=0 при трафике; неверные данные — ValueError. 4xx не входят в 5xx. `scenario.json` — числовой вход, не свидетельство работающего стенда.

```bash
docker compose -f labs/monitoring/compose.yaml up -d --build
make task TASK=09-monitoring/01-load-dashboard
```

Подключи обученный bundle, отправь 200 predict с concurrency=1 и 4, измерь duration, statuses и p95 выбранным HTTP-клиентом. Например, 200 ответов за 10 секунд дают 20 RPS; 10 ответов 503 дают error_ratio=0.05. Запросы /metrics не входят в бизнес-RPS.

В `dashboard.json` добавь latency/error panels и импортируй в Grafana на порту 3000. RPS: rate(counter); p95: histogram_quantile(0.95, sum by (le) (rate(bucket[5m]))); 5xx/all — отношение rates. Подожди несколько scrape intervals, сравни с клиентом. Не усредняй p95 экземпляров. Сохрани dashboard JSON как рабочий артефакт. После занятия `docker compose -f labs/monitoring/compose.yaml down`.

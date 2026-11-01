# Нагрузка и dashboard

## Зачем сравнивать клиент и dashboard

Увеличение concurrency, числа одновременно выполняемых запросов, может повысить throughput и одновременно ухудшить хвост задержек. Нужно сохранить измерения нагрузки и понять, какие из них Prometheus оценивает по другому временному окну. График без реальных predict-запросов этого не показывает.

Исходное состояние — готовая HTTP-инструментация API и Compose с Prometheus/Grafana. Для успешного predict нужен твой bundle в `work/artifacts`; в `solution.py` не реализован расчёт итогов. Связь компонентов смотри в [пути метрики](../../README.md#путь-запроса-и-путь-метрики), формулы — в [счётчиках и длительности](../../README.md#счётчики-длительность-и-запросы).

## Контракт функции и измерений

`run` содержит `concurrency`, `requests`, `seconds`, `status_counts` со строковыми HTTP-кодами и `p95_seconds`. Результат имеет только `rps`, `error_ratio`, `p95_seconds`. Например, 20 запросов за 4 секунды, из них два 503 и p95=.2, дают 5 RPS, .1 доли 5xx и .2 секунды p95. Функция обобщает уже измеренную p95, не восстанавливает её по счётчикам статусов. Ты реализуешь расчёт и проверки входа, затем редактируешь панели в `dashboard.json`; фиксированный scenario не является замером работающего API.

## Реализация и запуск

Реализуй `summarize_run(run)` в `solution.py`. Верни `rps=requests/seconds`, `error_ratio=5xx/requests`, `p95_seconds` без изменения. При нулевом трафике: rps=0, остальные два поля None. Требуй seconds>0, concurrency>=1, неотрицательные целые counts с суммой requests и p95>=0 при трафике; неверные данные — ValueError. 4xx не входят в 5xx. `scenario.json` — числовой вход, не свидетельство работающего стенда.

```bash
docker compose -f labs/monitoring/compose.yaml up -d --build
make task TASK=09-monitoring/01-load-dashboard
```

Подключи обученный bundle, отправь 200 predict с concurrency=1 и 4, измерь duration, statuses и p95 выбранным HTTP-клиентом. Например, 200 ответов за 10 секунд дают 20 RPS; 10 ответов 503 дают error_ratio=0.05. Запросы /metrics не входят в бизнес-RPS.

В `dashboard.json` добавь latency/error panels и импортируй в Grafana на порту 3000. RPS: rate(counter); p95: histogram_quantile(0.95, sum by (le) (rate(bucket[5m]))); 5xx/all — отношение rates. Подожди несколько scrape intervals, сравни с клиентом. Не усредняй p95 экземпляров. Сохрани dashboard JSON как рабочий артефакт. После занятия `docker compose -f labs/monitoring/compose.yaml down`.

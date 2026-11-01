# Нагрузка и dashboard

Реализуй `summarize_run(run)` в `solution.py`. Верни `rps=requests/seconds`, `error_ratio=5xx/requests`, `p95_seconds` без изменения. При нулевом трафике: rps=0, остальные два поля None. Требуй seconds>0, concurrency>=1, неотрицательные целые counts с суммой requests и p95>=0 при трафике; неверные данные — ValueError. 4xx не входят в 5xx. `scenario.json` — числовой вход, не свидетельство работающего стенда.

```bash
docker compose -f labs/monitoring/compose.yaml up -d --build
make task TASK=09-monitoring/01-load-dashboard
```

Подключи обученный bundle, отправь 200 predict с concurrency=1 и 4, измерь duration, statuses и p95 выбранным HTTP-клиентом. Например, 200 ответов за 10 секунд дают 20 RPS; 10 ответов 503 дают error_ratio=0.05. Запросы /metrics не входят в бизнес-RPS.

В `dashboard.json` добавь latency/error panels и импортируй в Grafana на порту 3000. RPS: rate(counter); p95: histogram_quantile(0.95, sum by (le) (rate(bucket[5m]))); 5xx/all — отношение rates. Подожди несколько scrape intervals, сравни с клиентом. Не усредняй p95 экземпляров. Dashboard JSON — рабочий артефакт; отдельный текстовый отчёт не нужен. После занятия `docker compose -f labs/monitoring/compose.yaml down`.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

# Мониторинг: нагрузка и dashboard

Зависит от обученного bundle и API. Не включай scrape /metrics в бизнес-RPS.

## Что редактировать

Реализуй предметные TODO в `solution.py`: входы и ожидаемые результаты перечислены ниже в разделе «Контракт и проверка» и в `test_task.py`. После практического опыта заполни `report.json` собственными наблюдениями по `report.template.json`.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов. Нужны Docker Compose, HTTP-клиент; внешнего monitoring SDK не требуется.

Останови конфликтующий API и при необходимости kind. `docker compose -f labs/monitoring/compose.yaml up -d --build`. Подключи свой bundle, проверь Prometheus 9090, Grafana 3000 (student / local-course-only), targets и свежесть samples. Отправь по 200 predict с ограниченной конкурентностью 1 и 4, сохрани duration/statuses/p95. Добавь панели latency/errors в task-local dashboard.json и импортируй в Grafana. RPS — rate(counter), p95 — histogram_quantile по сумме buckets, error ratio — 5xx/all. Подожди несколько scrape intervals. Сравни клиентские измерения с панелями; не усредняй p95 экземпляров.

Проверка выбранного задания:

```bash
make task TASK=09-monitoring/01-load-dashboard
python scripts/run_task.py run 09-monitoring/01-load-dashboard -- --report modules/09-monitoring/tasks/01-load-dashboard/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`summarize_run(run) -> dict`: вернуть requests/seconds как rps, число 5xx/requests как error_ratio (4xx не считать 5xx), p95_seconds без изменений. При requests=0 вернуть rps=0, error_ratio=None, p95_seconds=None. Требуй seconds>0, concurrency>=1, неотрицательные целые status_counts с суммой requests, p95>=0 при трафике. `validate_report(report) -> {"runs": [summary,...]}` требует ровно concurrency 1/4 по 200 запросов, корректный target/datasource/route, scrape_up=1 и три панели.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

Экспортируй dashboard JSON/отчёт до `docker compose -f labs/monitoring/compose.yaml down`.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

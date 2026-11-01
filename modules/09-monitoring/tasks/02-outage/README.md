# Отказ и восстановление

Редактируй `rules.yaml`: добавь отдельное правило для живого API без модели (readiness либо predict 5xx). Начни с копии labs/monitoring/alerts.yml в rules.yaml, сохрани HousingTargetDown и добавь своё правило. Для подключения создай task-local compose.override.yaml с volume `./rules.yaml:/etc/prometheus/alerts.yml:ro` для services.prometheus (пути Compose привязаны к первому compose-файлу; удобнее использовать абсолютный путь к rules.yaml). Основное правило HousingTargetDown уже есть в labs/monitoring/alerts.yml. Перед запуском проверь файл командой `docker run --rm --entrypoint promtool -v "$PWD/modules/09-monitoring/tasks/02-outage/rules.yaml:/tmp/rules.yaml:ro" prom/prometheus:v3.2.1 check rules /tmp/rules.yaml`.

```bash
docker compose -f labs/monitoring/compose.yaml -f modules/09-monitoring/tasks/02-outage/compose.override.yaml up -d --build
curl -fsS 'http://127.0.0.1:9090/api/v1/query?query=up%7Bjob%3D%22housing%22%7D'
MLOPS_RUN_INTEGRATION=1 make task TASK=09-monitoring/02-outage
# Только вручную для опыта отказа:
docker compose -f labs/monitoring/compose.yaml stop api
MLOPS_RUN_INTEGRATION=1 MLOPS_EXPECT_UP=0 make task TASK=09-monitoring/02-outage
curl -fsS http://127.0.0.1:9090/api/v1/alerts
docker compose -f labs/monitoring/compose.yaml start api
```

Подожди scrape interval после stop/start и дольше `for` правила для firing. Ожидаемый инвариант: up 1→0→1, alert inactive→pending→firing→inactive. Firing не подтверждает доставку уведомления. Проверь вручную /ready и /predict в варианте без bundle: up=1 при HTTP503, поэтому одного up недостаточно. `PROMETHEUS_URL` меняет адрес live-проверки. Она проверяет текущий target и загруженные правила, не историю переходов. Текстовый отчёт не требуется. В конце `docker compose -f labs/monitoring/compose.yaml down`.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

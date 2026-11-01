# Отказ и восстановление

## Зачем нужны два сигнала отказа

Недоступный процесс и живой API без модели требуют разных диагностических действий. Prometheus видит успешный `/metrics` даже тогда, когда predict возвращает 503. Поэтому правило target down нужно сохранить, а отказ полезной функции — обнаружить отдельным сигналом.

Уже готовы Compose, scrape каждые 5 секунд и `HousingTargetDown`. Ты создаёшь task-local rules и подключающий override, не меняя общий стенд. Нужны [различие уровней здоровья](../../README.md#три-уровня-здоровья-и-качество-модели) и [состояния alert](../../README.md#алерты-и-поиск-причины).

## Технический контракт

На живом процессе ожидается `up=1`, после остановки и очередного scrape — `up=0`, после запуска — снова 1. Для условия, выдержавшего `for`, alert проходит pending→firing. Вариант без модели сохраняет `up=1`, но должен обнаруживаться дополнительным правилом. Например, серия реальных predict с HTTP503 увеличивает существующий счётчик 5xx; для отдельной readiness-метрики нужен её источник, в API готового gauge нет. Live-тест читает текущий up и загруженные правила, не доказывает историю переходов или доставку уведомлений.

## Настройка и опыт отказа

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

Подожди scrape interval после stop/start и дольше `for` правила для firing. Ожидаемый инвариант: up 1→0→1, alert inactive→pending→firing→inactive. Firing не подтверждает доставку уведомления. Проверь вручную /ready и /predict в варианте без bundle: up=1 при HTTP503, поэтому одного up недостаточно. `PROMETHEUS_URL` меняет адрес live-проверки. Она проверяет текущий target и загруженные правила, не историю переходов. В конце `docker compose -f labs/monitoring/compose.yaml down`.

# Отказ и восстановление

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем нужны два сигнала отказа

Недоступный процесс и живой API без модели требуют разных диагностических действий. Prometheus видит успешный `/metrics` даже тогда, когда predict возвращает 503. Поэтому правило target down нужно сохранить, а отказ полезной функции — обнаружить отдельным сигналом.

Уже готовы Compose, scrape каждые 5 секунд и `HousingTargetDown`. Ты создаёшь task-local rules и подключающий override, не меняя общий стенд. Нужны [различие уровней здоровья](../../README.md#три-уровня-здоровья-и-качество-модели) и [состояния alert](../../README.md#алерты-и-поиск-причины).

## Файлы и параметры проверки

| Вход | Тип и формат | Происхождение и действие | Пример |
|---|---|---|---|
| `rules.yaml` | YAML Prometheus с `groups[].rules[]` | Task-local заготовка пустая. Скопируй основной HousingTargetDown и добавь свой alert | `alert`, `expr`, `for`, `labels` |
| `alert` | Строка имени | Отличает своё правило от базового | Собственное имя для predict 5xx |
| `expr` | PromQL-строка | Условие по реально экспортируемой метрике | Счётчик `/predict` с `status=~"5.."` |
| `for` | Строка длительности | Условие должно держаться этот период до firing | `30s` в базовом правиле |
| Новый `compose.override.yaml` | YAML Compose | Переопределяет volume rules для `services.prometheus`, общий Compose не редактируется | Абсолютный путь rules → `/etc/prometheus/alerts.yml:ro` |
| `PROMETHEUS_URL` | URL в env теста, default `http://127.0.0.1:9090` | Адрес HTTP API Prometheus на компьютере | `http://127.0.0.1:9090` |
| `MLOPS_EXPECT_UP` | Строка `"0"` или `"1"`, default `"1"` | Текущее ожидаемое состояние target в read-only тесте | `0` после stop и scrape |

Пути относительных bind mounts Compose вычисляет от первого `-f`, то есть каталога `labs/monitoring`. Абсолютный путь к task-local rules помогает избежать чтения другого файла. Тест проверяет наличие загруженного основного и дополнительного alert, но не доказывает правильность выражения дополнительного правила. Его срабатывание проверь настоящими запросами и `/api/v1/alerts`.

## Технический контракт

На живом процессе ожидается `up=1`, после остановки и очередного scrape — `up=0`, после запуска — снова 1. Для условия, выдержавшего `for`, alert проходит pending→firing. Вариант без модели сохраняет `up=1`, но должен обнаруживаться дополнительным правилом. Например, серия реальных predict с HTTP503 увеличивает существующий счётчик 5xx. Для отдельной readiness-метрики нужен её источник, в API готового gauge нет. Live-тест читает текущий up и загруженные правила, не доказывает историю переходов или доставку уведомлений.

## Настройка и опыт отказа

Редактируй `rules.yaml`: начни с копии `labs/monitoring/alerts.yml`, сохрани `HousingTargetDown` и добавь своё правило для живого API без модели. Оно может использовать predict 5xx. Для readiness нужен реальный источник метрики, готового gauge в API нет.

Создай рядом `compose.override.yaml`, который подключит этот rules-файл к `services.prometheus` как `/etc/prometheus/alerts.yml:ro`. Используй абсолютный путь к исходному файлу на компьютере, чтобы не перепутать базовый каталог Compose. Общие файлы в `labs/monitoring` менять не требуется.

Проверь синтаксис rules перед запуском:

```bash
docker run --rm --entrypoint promtool -v "$PWD/modules/09-monitoring/tasks/02-outage/rules.yaml:/tmp/rules.yaml:ro" prom/prometheus:v3.2.1 check rules /tmp/rules.yaml
```

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

## Отдельный опыт без модели

Для воспроизведения состояния без bundle сохрани свою модель на месте, а через task-local Compose override направь volume API `/models:ro` на отдельный пустой каталог, например `work/monitoring-empty-models`. Создай этот каталог до запуска. Как и для rules, абсолютный путь источника исключает неоднозначность Compose. Пересоздай только API через ту же пару `-f` и `up -d --force-recreate api`.

После правки своего override:

```bash
docker compose -f labs/monitoring/compose.yaml -f modules/09-monitoring/tasks/02-outage/compose.override.yaml up -d --force-recreate api
curl -i http://127.0.0.1:8000/ready
curl -i -H 'Content-Type: application/json' --data @labs/housing/request.json http://127.0.0.1:8000/predict
```

Теперь `/live` и `/metrics` должны отвечать, `/ready` и корректный `/predict` — давать 503. Если выбрано правило по 5xx, создай реальные predict-запросы с `labs/housing/request.json` и наблюдай alerts после своего `for`. Один up=1 не подтверждает готовность. Затем верни исходный mount `work/artifacts:/models:ro` в своём override и пересоздай API, чтобы восстановить рабочую модель. В конце останови ту же конфигурацию с обоими `-f`:

```bash
docker compose -f labs/monitoring/compose.yaml -f modules/09-monitoring/tasks/02-outage/compose.override.yaml down
```

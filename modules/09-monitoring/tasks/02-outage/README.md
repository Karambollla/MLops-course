# Обнаружить два разных отказа API

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

Нагрузка видна в Prometheus. Теперь надо различить два случая: процесс API остановлен и процесс работает, но не загрузил модель. В первом случае Prometheus не получит метрики. Во втором `/metrics` доступен, а `/predict` возвращает 503. Одно правило по `up` не обнаружит оба отказа.

В общем стенде уже есть scrape каждые 5 секунд и `HousingTargetDown`. Ты заполнишь соседний [rules.yaml](rules.yaml) и создашь `compose.override.yaml` в каталоге задания, чтобы подключить свой файл правил. Общие конфиги `labs/monitoring` менять не требуется. Python-функции здесь нет. Состояния alert объясняются в [главе](../../README.md#алерты-и-поиск-причины).

## Шаг 1. Подключить два правила

Скопируй содержимое `labs/monitoring/alerts.yml` в `rules.yaml`: базовое правило `HousingTargetDown` должно сохраниться. Добавь alert с другим именем для серверных ошибок `/predict`. Используй существующий `http_requests_total` с `route="/predict"` и `status=~"5.."`, а не вымышленный gauge readiness: API его не экспортирует.

Поля `groups[].rules[]` задают имя `alert`, условие `expr`, период `for` и дополнительные `labels`. Сначала реши, какое наблюдение считать отказом: например, наличие 5xx predict на выбранном временном окне. Затем запиши PromQL и период устойчивости условия. Правило на основе трафика требует настоящих predict-запросов: отсутствие запросов не доказывает готовность модели.

В новом `compose.override.yaml` переопредели volume `services.prometheus`, подключив свой `rules.yaml` как `/etc/prometheus/alerts.yml:ro`. Источник должен указывать на файл задания на компьютере. Относительные bind mounts считаются от первого `-f`, то есть `labs/monitoring`. Абсолютный путь помогает не прочитать другой файл.

Например, при запуске из корня курса `PWD` указывает на каталог проекта, и override может подключить rules так:

```yaml
services:
  prometheus:
    volumes:
      - ${PWD}/modules/09-monitoring/tasks/02-outage/rules.yaml:/etc/prometheus/alerts.yml:ro
```

Проверь rules отдельно:

```bash
docker run --rm --entrypoint promtool -v "$PWD/modules/09-monitoring/tasks/02-outage/rules.yaml:/tmp/rules.yaml:ro" prom/prometheus:v3.2.1 check rules /tmp/rules.yaml
```

Затем запусти конфигурацию с override:

```bash
docker compose -f labs/monitoring/compose.yaml -f modules/09-monitoring/tasks/02-outage/compose.override.yaml up -d --build
MLOPS_RUN_INTEGRATION=1 make task TASK=09-monitoring/02-outage
```

Тест ожидает `up=1`, наличие базового и ещё одного alert в `/api/v1/rules`. Он не оценивает смысл дополнительного выражения и не доказывает его срабатывание. Это проверяется следующими опытами.

## Шаг 2. Остановить и восстановить процесс

```bash
docker compose -f labs/monitoring/compose.yaml -f modules/09-monitoring/tasks/02-outage/compose.override.yaml stop api
```

Подожди очередного scrape, затем проверь текущий отказ:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_EXPECT_UP=0 make task TASK=09-monitoring/02-outage
curl -fsS http://127.0.0.1:9090/api/v1/alerts
```

`MLOPS_EXPECT_UP` принимает строку `0` или `1`, по умолчанию `1`. После неуспешного scrape ожидается `up=0`, затем `HousingTargetDown` проходит pending и после устойчивого условия `for: 30s` — firing. Учитывай также периоды scrape/evaluation. Firing означает вычисленный сигнал. Доставки уведомления в этом стенде нет.

```bash
docker compose -f labs/monitoring/compose.yaml -f modules/09-monitoring/tasks/02-outage/compose.override.yaml start api
```

После успешного scrape ожидаются `up=1` и исчезновение активного базового alert. Повтори тест с обычным `MLOPS_EXPECT_UP=1`. `PROMETHEUS_URL` меняет базовый URL проверки, по умолчанию `http://127.0.0.1:9090`. Тест проверяет текущее состояние, а переходы ты наблюдаешь сам.

## Шаг 3. Оставить процесс без модели

Свою модель не удаляй. Создай пустой `work/monitoring-empty-models` и в том же task-local override направь volume API `/models:ro` на абсолютный путь этого каталога. Это заменяет только источник bundle. Затем пересоздай API:

```bash
mkdir -p work/monitoring-empty-models
docker compose -f labs/monitoring/compose.yaml -f modules/09-monitoring/tasks/02-outage/compose.override.yaml up -d --force-recreate api
curl -i http://127.0.0.1:8000/ready
curl -i -H 'Content-Type: application/json' --data @labs/housing/request.json http://127.0.0.1:8000/predict
```

Ожидаются работающие `/live` и `/metrics`, но HTTP 503 для `/ready` и корректного `/predict`. После scrape `up` остаётся равным 1. Повтори реальные predict-запросы так, чтобы условие твоего правила сохранялось до `for`, и наблюдай дополнительный alert в `/api/v1/alerts`. Проверь, что базовое правило не подменяет этот сигнал.

Для классификатора изображений отсутствие файла весов дало бы похожий технический отказ. Ошибочный класс при HTTP 200 потребовал бы другой проверки — известных правильных меток, как в следующем задании требуется target для Housing.

## Восстановление и завершение

Верни в override исходный mount `work/artifacts:/models:ro`, пересоздай API той же парой `-f` и проверь `/ready` и `/predict`. Alert по 5xx может оставаться активным, пока ошибки ещё входят в его временное окно. Это отличается от продолжающегося отказа.

Останови ту же конфигурацию:

```bash
docker compose -f labs/monitoring/compose.yaml -f modules/09-monitoring/tasks/02-outage/compose.override.yaml down
```

Bundle в `work/artifacts` сохраняется. Файлы rules и override остаются исходниками опыта. Named volumes Prometheus/Grafana при `down` не удаляются.

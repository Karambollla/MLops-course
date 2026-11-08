# Kubernetes: живой, но неготовый API

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Что предстоит сделать

Сервис может принимать HTTP-соединения, но не иметь модели для полезного ответа. В этом опыте отсутствие bundle намеренно: нужно увидеть, как Kubernetes отделяет живой контейнер от допустимого получателя трафика. Простое повторение restart не создаст отсутствующую модель.

Примени соседний [deployment.yaml](deployment.yaml) без изменения образа `housing:course`, затем проверь состояние Pod, адреса Service и ответы двух обработчиков. Манифест уже задаёт нужную конфигурацию. Здесь ты подготавливаешь и исследуешь состояние без bundle. Код API уже реализует `/live` и `/ready`. Писать обработчики или обучать модель здесь не требуется. Разбери [путь запроса к Service](../../README.md#как-запрос-находит-готовую-модель) и [смысл probes](../../README.md#probes-конфигурация-и-хранение).

## Как читать `deployment.yaml`

В [deployment.yaml](deployment.yaml) находятся два YAML-документа, разделённые `---`: Deployment `housing` и Service `housing`. Это конфигурационное задание без учебной Python-функции. Менять готовые HTTP-обработчики и тесты не требуется.

| Поле | Тип и формат | Происхождение, смысл и пример |
|---|---|---|
| `spec.replicas` Deployment | Положительное целое | Желаемое количество Pod, исходно `1` |
| `spec.selector.matchLabels`, `spec.template.metadata.labels`, Service `spec.selector` | Карты меток | Согласованный выбор экземпляров, в заготовке `app: housing` |
| `containers[].name` и `image` | Строки | Имя `api` используется в `set image`. Image выбирает выпуск кода и модели |
| `imagePullPolicy` | Строка Kubernetes | `Never` требует заранее загрузить точный тег в kind |
| `env[].name`, `env[].value` | Строки | `MODEL_PATH=/models/model.joblib` — путь внутри контейнера. Файла на компьютере по такому пути не требуется |
| `resources.requests`, `resources.limits` | Карты CPU/memory quantities | `100m` = 0.1 CPU, `128Mi` = 128 MiB. Сохрани ограничения из заготовки |
| `livenessProbe.httpGet`, `readinessProbe.httpGet` | Объекты с path/port | `/live` и `/ready` на порту `8000` проверяют разные состояния |
| Service `ports[].port`, `targetPort` | Числа портов | `8000` сервиса пересылается на `8000` контейнера |

`kubectl apply -f <путь>` читает файл на компьютере и меняет объекты выбранного контекста/namespace. Тест получает их через `kubectl get -o json` и ничего не применяет. Общие env-переменные и различие URL/контекста описаны в [подготовке модуля](../../README.md#подготовка-к-заданиям).

В этом задании оставь `image: housing:course` без файла модели. Готовая заготовка уже задаёт нужные probes и selector. Задача — подготовить и исследовать это состояние, а не исправить ожидаемый 503 добавлением модели.

## Технический контракт

Контейнер `api` использует `housing:course`, liveness `/live`, readiness `/ready`. Service выбирает `app=housing`. Выход — наблюдаемое состояние Running при Ready 0/1, HTTP 200 на `/live`, HTTP 503 на `/ready` и отсутствие готового endpoint Service. Например, прямой port-forward позволяет получить `/live → {"status":"alive"}` при том, что Service ещё не имеет готового адреса. Это ожидаемый учебный результат, а не ошибка, которую надо скрыть заменой probe.

## Подготовка и проверка

Используй кластер, активную среду и `MLOPS_KUBE_CONTEXT`/`MLOPS_KUBE_NAMESPACE`/`MLOPS_API_URL` из [подготовки модуля](../../README.md#подготовка-к-заданиям), в том числе в терминале pytest. Команды ниже меняют твои ресурсы. Тесты только читают подготовленное состояние.

Используй базовый образ без модели, не заменяй readiness на /live.

```bash
docker build -t housing:course -f labs/housing/Dockerfile .
kind load docker-image housing:course --name mlops-course
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" apply -f modules/07-kubernetes/tasks/01-unready/deployment.yaml
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" get pods -l app=housing
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" describe pods -l app=housing
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" get endpointslices -l kubernetes.io/service-name=housing -o yaml
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" port-forward deployment/housing 8000:8000
```

Последняя команда — в отдельном терминале после старта процесса. Затем:

```bash
curl --max-time 10 -i "$MLOPS_API_URL/live"
curl --max-time 10 -i "$MLOPS_API_URL/ready"
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/07-kubernetes/tasks/01-unready/test_task.py -q
```

Ожидаемая картина: Pod находится в состоянии Running, но показывает READY 0/1. Прямой запрос к `/live` возвращает 200, к `/ready` — 503. В событиях видны неуспешные readiness-проверки, а у Service нет готового endpoint. Прямой port-forward к Pod даёт доступ к живому процессу и не доказывает маршрутизацию Service. После стабилизации ожидается 1 passed. Без флага — 1 skipped с инструкцией. С флагом отсутствие CLI/контекста/API вызывает failure. Останови port-forward перед переходом к 02. Кластер оставь.

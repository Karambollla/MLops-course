# Kubernetes: живой, но неготовый API

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем наблюдать неготовый процесс

Сервис может принимать HTTP-соединения, но не иметь модели для полезного ответа. В этом опыте отсутствие bundle намеренно: нужно увидеть, как Kubernetes отделяет живой контейнер от допустимого получателя трафика. Простое повторение restart не создаст отсутствующую модель.

Исходное состояние — базовый `housing:course`, собственный kind и task-local Deployment/Service. Код API уже реализует `/live` и `/ready`. Писать обработчики или обучать модель здесь не требуется. Разбери [путь запроса к Service](../../README.md#как-запрос-находит-готовую-модель) и [смысл probes](../../README.md#probes-конфигурация-и-хранение).

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

Контейнер `api` использует `housing:course`, liveness `/live`, readiness `/ready`. Service выбирает `app=housing`. Выход — наблюдаемое состояние Running при Ready 0/1, HTTP200 на `/live`, HTTP503 на `/ready` и отсутствие готового endpoint Service. Например, прямой port-forward позволяет получить `/live → {"status":"alive"}` при том, что Service ещё не имеет готового адреса. Это ожидаемый учебный результат, а не ошибка, которую надо скрыть заменой probe.

## Подготовка и проверка

Нужны Docker daemon, kind, kubectl. Python Kubernetes SDK не нужен.
`MLOPS_KUBE_CONTEXT` обязателен: тесты не используют текущий контекст.
Команды подготовки изменяют только твой учебный кластер. Pytest только читает.
Для каждого задания подготовь указанное состояние отдельно, не запускай все live
тесты одной командой: состояния 01 и 02 несовместимы.

```bash
export MLOPS_KUBE_CONTEXT=kind-mlops-course
export MLOPS_KUBE_NAMESPACE=default
export MLOPS_API_URL=http://127.0.0.1:8000
```

Если кластер ещё не создан: `kind create cluster --name mlops-course` по SETUP.
Все манифесты ниже — task-local. `labs/kubernetes/deployment.yaml` не используется.

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

Ожидаемая картина: Pod находится в состоянии Running, но показывает READY 0/1.
Прямой запрос к `/live` возвращает 200, к `/ready` — 503. В событиях видны
неуспешные readiness-проверки, а у Service нет готового endpoint. Прямой port-forward к Pod
даёт доступ к живому процессу и не доказывает маршрутизацию Service.
После стабилизации ожидается 1 passed. Без флага — 1 skipped с инструкцией.
С флагом отсутствие CLI/контекста/API вызывает failure.
Останови port-forward перед переходом к 02. Кластер оставь.

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы ниже иллюстрируют инварианты. Это не запись успешного выполнения.

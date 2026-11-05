# Kubernetes: рабочий выпуск

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем поставлять код и модель вместе

После предыдущего опыта процесс жив, но предсказывать нечем. Теперь нужно выпустить конкретный собственный bundle и доказать, что запросы обслуживает именно он. Одного Ready недостаточно: при ошибке выбора image можно получить готовую старую модель.

На входе нужны обученный и экспортированный `work/artifacts/model.joblib`, базовый `housing:course` и кластер из задания 01. `Dockerfile.model` уже задаёт копирование bundle, API уже реализован. Ты меняешь task-local манифест: image, обычную конфигурацию и её подключение. Происхождение файлов объясняется в [поставке модели](../../README.md#разобранный-манифест-и-поставка-модели), связь объектов — в [пути HTTP-запроса](../../README.md#как-запрос-находит-готовую-модель).

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

Для рабочего выпуска измени image на `housing:v1`. Добавь YAML-документ ConfigMap с собственными строковыми несекретными `data` и подключи его через `containers[].envFrom[].configMapRef.name`. Например, обычный ключ `COURSE_MODE: release` позволяет наблюдать доставку env. Имя ссылки должно совпадать с `metadata.name` ConfigMap. Выбор ключа остаётся твоим.

Образ `housing:v1` собирается `labs/kubernetes/Dockerfile.model` из базового `housing:course` и твоего bundle на компьютере. В контейнере bundle окажется именно в `/models/model.joblib`. Тест проверяет текущую готовность и версию, а историю редактирования ConfigMap наблюдай отдельно.

## Технический контракт

Нужны `housing:v1`, ConfigMap через envFrom, отдельные probes и сохранённые requests/limits. Выход — все требуемые реплики обновлены и готовы, у Pod есть imageID, Service имеет ready endpoint. Запрос `instances` из `labs/housing/request.json` даёт HTTP200, столько же `predictions` и ожидаемую `model_version`. Например, для двух instance должно быть два прогноза. Сами числа зависят от твоей модели. Ожидаемая версия берётся из bundle до запроса, не копируется из ответа API.

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

Заверши обучение и экспорт bundle из 01–03 в `work/artifacts/`.
В task-local `deployment.yaml` замени image на housing:v1, добавь собственный
ConfigMap с обычной настройкой, подключи его через envFrom. Сохрани requests/limits
и разные probes. Не добавляй готовую модель в базовый образ course.

```bash
docker build -t housing:v1 -f labs/kubernetes/Dockerfile.model .
kind load docker-image housing:v1 --name mlops-course
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" apply -f modules/07-kubernetes/tasks/02-release/deployment.yaml
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout status deployment/housing --timeout=120s
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" get pods -l app=housing -o wide
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" get endpointslices -l kubernetes.io/service-name=housing -o yaml
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" port-forward service/housing 8000:8000
```

Последняя команда — в отдельном терминале. Узнай ожидаемую версию своего доверенного
bundle (joblib загружай только свой), передай её независимо от HTTP ответа:

```bash
export MLOPS_EXPECTED_MODEL_VERSION="$(python -c 'import joblib; print(joblib.load("work/artifacts/model.joblib")["model_version"])')"
curl --fail --max-time 10 "$MLOPS_API_URL/ready"
curl --fail --max-time 10 -H 'Content-Type: application/json' --data @labs/housing/request.json "$MLOPS_API_URL/predict"
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/07-kubernetes/tasks/02-release/test_task.py -q
```

Иллюстрация: READY 1/1, deployment updated/ready равны desired, imageID непустой,
ready endpoints >=1. Predict HTTP200 с predictions для каждого instance и
model_version, равной своему bundle. Ожидается 1 passed. Без флага 1 skipped.
Тест не проверяет историю изменения env. Для этого измени свою обычную настройку
ConfigMap и примени манифест: старый Pod сохраняет прежнее env.
После `kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout restart deployment/housing`
и rollout status новый Pod получит новую настройку. Проверь только свой несекретный
ключ через printenv (не весь env): имя ConfigMap/ключ выбери в собственном манифесте.
Сохрани image v1 для отката, останови port-forward.

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы ниже иллюстрируют инварианты. Это не запись успешного выполнения.

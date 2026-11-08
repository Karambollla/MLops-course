# Kubernetes: рабочий выпуск

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Что предстоит сделать

После предыдущего опыта процесс жив, но предсказывать нечем. Теперь нужно выпустить конкретный собственный bundle и доказать, что запросы обслуживает именно он. Одного Ready недостаточно: при ошибке выбора image можно получить готовую старую модель.

На входе нужны обученный и экспортированный `work/artifacts/model.joblib`, базовый `housing:course` и кластер из задания 01. `Dockerfile.model` уже задаёт копирование bundle, API уже реализован. В соседнем [deployment.yaml](deployment.yaml) измени image, добавь обычную конфигурацию и её подключение. Собери образ с bundle, дождись готовности экземпляров и сравни `model_version` HTTP-ответа с версией собственного файла. Происхождение файлов объясняется в [поставке модели](../../README.md#разобранный-манифест-и-поставка-модели), связь объектов — в [пути HTTP-запроса](../../README.md#как-запрос-находит-готовую-модель).

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

Нужны `housing:v1`, ConfigMap через envFrom, отдельные probes и сохранённые requests/limits. Выход — все требуемые реплики обновлены и готовы, у Pod есть imageID, Service имеет ready endpoint. Запрос `instances` из `labs/housing/request.json` даёт HTTP 200, столько же `predictions` и ожидаемую `model_version`. Например, для двух instance должно быть два прогноза. Сами числа зависят от твоей модели. Ожидаемая версия берётся из bundle до запроса, не копируется из ответа API.

## Подготовка и проверка

Используй кластер, активную среду и `MLOPS_KUBE_CONTEXT`/`MLOPS_KUBE_NAMESPACE`/`MLOPS_API_URL` из [подготовки модуля](../../README.md#подготовка-к-заданиям), в том числе в терминале pytest. Команды ниже меняют твои ресурсы. Тесты только читают подготовленное состояние.

После изменений манифеста собери отдельный `housing:v1`: базовый `housing:course` остаётся образом без модели. Команда сборки читает экспортированный `work/artifacts/model.joblib`.

```bash
docker build -t housing:v1 -f labs/kubernetes/Dockerfile.model .
kind load docker-image housing:v1 --name mlops-course
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" apply -f modules/07-kubernetes/tasks/02-release/deployment.yaml
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout status deployment/housing --timeout=120s
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" get pods -l app=housing -o wide
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" get endpointslices -l kubernetes.io/service-name=housing -o yaml
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" port-forward service/housing 8000:8000
```

Последняя команда — в отдельном терминале. Узнай ожидаемую версию своего доверенного bundle (joblib загружай только свой), передай её независимо от HTTP ответа:

```bash
export MLOPS_EXPECTED_MODEL_VERSION="$(python -c 'import joblib; print(joblib.load("work/artifacts/model.joblib")["model_version"])')"
curl --fail --max-time 10 "$MLOPS_API_URL/ready"
curl --fail --max-time 10 -H 'Content-Type: application/json' --data @labs/housing/request.json "$MLOPS_API_URL/predict"
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/07-kubernetes/tasks/02-release/test_task.py -q
```

При одной реплике ожидается `READY 1/1`. Числа обновлённых и готовых реплик равны желаемому. `imageID` подтверждает запущенный образ, у Service есть хотя бы один готовый адрес. `/predict` возвращает HTTP 200, по прогнозу на каждую входную строку и версию собственного bundle. Ожидается 1 passed. Без флага 1 skipped. Тест не проверяет историю изменения env. Для этого измени свою обычную настройку ConfigMap и примени манифест: старый Pod сохраняет прежнее env. После `kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout restart deployment/housing` и rollout status новый Pod получит новую настройку. Проверь только свой несекретный ключ через printenv (не весь env): имя ConfigMap/ключ выбери в собственном манифесте. Сохрани image v1 для отката, останови port-forward.

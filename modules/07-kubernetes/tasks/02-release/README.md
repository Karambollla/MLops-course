# Kubernetes: рабочий выпуск

Нужны Docker daemon, kind, kubectl; Python Kubernetes SDK не нужен.
`MLOPS_KUBE_CONTEXT` обязателен: тесты не используют текущий контекст.
Команды подготовки изменяют только твой учебный кластер; pytest только читает.
Для каждого задания подготовь указанное состояние отдельно, не запускай все live
тесты одной командой: состояния 01 и 02 несовместимы.

```bash
export MLOPS_KUBE_CONTEXT=kind-mlops-course
export MLOPS_KUBE_NAMESPACE=default
export MLOPS_API_URL=http://127.0.0.1:8000
```

Если кластер ещё не создан: `kind create cluster --name mlops-course` по SETUP.
Все манифесты ниже — task-local; `labs/kubernetes/deployment.yaml` не используется.

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
ready endpoints >=1; predict HTTP200 с predictions для каждого instance и
model_version, равной своему bundle. Ожидается 1 passed; без флага 1 skipped.
Тест не проверяет историю изменения env. Для этого измени свою обычную настройку
ConfigMap и примени манифест: старый Pod сохраняет прежнее env.
После `kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout restart deployment/housing`
и rollout status новый Pod получит новую настройку. Проверь только свой несекретный
ключ через printenv (не весь env): имя ConfigMap/ключ выбери в собственном манифесте.
Сохрани image v1 для отката, останови port-forward.

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы ниже иллюстрируют инварианты; это не запись успешного выполнения.
Отчёт, JSON-подтверждение и письменное описание не требуются.
[Теория](../../README.md) · [Подсказки](../../hints.md)

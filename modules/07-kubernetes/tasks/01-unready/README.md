# Kubernetes: живой, но неготовый API

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

Иллюстрация: Pod Running, READY 0/1; /live HTTP200, /ready HTTP503,
readiness events и ни одного ready endpoint Service. Прямой port-forward к Pod
даёт доступ к живому процессу и не доказывает маршрутизацию Service.
После стабилизации ожидается 1 passed. Без флага — 1 skipped с инструкцией;
с флагом отсутствие CLI/контекста/API вызывает failure.
Останови port-forward перед переходом к 02; кластер оставь.

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы ниже иллюстрируют инварианты; это не запись успешного выполнения.
Отчёт, JSON-подтверждение и письменное описание не требуются.
[Теория](../../README.md) · [Подсказки](../../hints.md)

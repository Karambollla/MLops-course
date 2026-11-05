# Kubernetes: сбой и восстановление

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем проверять неудачную выкладку

Ошибочный новый образ не обязательно сразу прекращает обслуживание: RollingUpdate может сохранить старую готовую реплику. Здесь важно отдельно увидеть причину незавершённого обновления и проверить, что откат вернул нужный выпуск, а не просто зелёный статус.

Исходное состояние — рабочий `housing:v1` из задания 02 с сохранённым образом в kind и известной model_version. Это руководство меняет существующий Deployment. Лежащий рядом манифест нужен только для дополнительных опытов. Механизм разобран в [обновлении и диагностике](../../README.md#обновление-откат-и-диагностика).

## Что изменяется в опыте

Основной опыт использует уже установленный Deployment из 02. `kubectl set image deployment/housing api=housing:missing` меняет поле image контейнера `api` в кластере. Локальный `deployment.yaml` от этой команды не переписывается. Соседний манифест — baseline для дополнительных опытов со startupProbe/PVC, а не готовый рабочий v1 для основного сценария.

`rollout history` возвращает доступные ревизии. `rollout undo` без `--to-revision` выбирает предыдущее состояние шаблона, поэтому после дополнительных изменений выбирай явную рабочую ревизию. Результат опыта проверяется тестом задания 02: отдельной функции или теста истории отказа здесь нет.

## Технический контракт

Подмена image на `housing:missing` должна дать ошибку rollout. При `Never` ожидается ErrImageNeverPull в событиях нового Pod. После undo — снова `housing:v1`, готовность и `/predict` с первоначальной версией. Например, «rollout завершился по timeout, старый predict ещё 200» является согласованным состоянием: доступность старого и успешность нового выпуска различаются. Тест 02 проверит восстановленный результат. Историческую причину проверяешь по events непосредственно при отказе.

## Ход опыта

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

Начни с рабочего v1 из 02, а не с model-less состояния 01.
`deployment.yaml` рядом — исходный baseline для дополнительного опыта со startupProbe/PVC.
основная последовательность ниже меняет существующий Deployment 02.

```bash
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout history deployment/housing
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" set image deployment/housing api=housing:missing
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout status deployment/housing --timeout=60s
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" describe pods -l app=housing
```

Иллюстрация: rollout status даёт ненулевой exit. Новый Pod с imagePullPolicy Never
имеет ErrImageNeverPull. Старый Ready Pod может продолжать обслуживать запросы
во время неудачного RollingUpdate. При Always/IfNotPresent ожидай другую ошибку
скачивания. Pending/CrashLoopBackOff/OOMKilled имеют другие причины.

```bash
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout undo deployment/housing
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout status deployment/housing --timeout=120s
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/07-kubernetes/tasks/02-release/test_task.py -q
```

Перед последней командой заново запусти Service port-forward и укажи ожидаемую v1
model_version по README 02. Инварианты восстановления: image housing:v1,
READY 1/1, predict HTTP200 и прежняя модель. Если история содержит другие изменения,
выбери явный `--to-revision` из history. Автотест 02 проверяет текущее состояние,
а причину предшествующего отказа наблюдай непосредственно в describe/events.
Дополнительно исследуй startupProbe и PVC. Диск Pod не становится постоянным от restart.
Перед Helm удали свои ресурсы командой delete -f с манифестом 02, останови forwarding.

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы ниже иллюстрируют инварианты. Это не запись успешного выполнения.

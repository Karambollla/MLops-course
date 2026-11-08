# Kubernetes: сбой и восстановление

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Что предстоит сделать

Ошибочный новый образ не обязательно сразу прекращает обслуживание: RollingUpdate может сохранить старую готовую реплику. Здесь важно отдельно увидеть причину незавершённого обновления и проверить, что откат вернул нужный выпуск, а не просто зелёный статус.

Исходное состояние — рабочий `housing:v1` из задания 02 с сохранённым образом в kind и известной model_version. В этом руководстве командой `kubectl set image` ты изменишь существующий Deployment, проверишь ошибку нового Pod, затем вернёшь рабочую ревизию и повторишь HTTP-проверку. Локальный YAML команда не редактирует. Лежащий рядом манифест нужен только для дополнительных опытов. Механизм разобран в [обновлении и диагностике](../../README.md#обновление-откат-и-диагностика).

## Что изменяется в опыте

Основной опыт использует уже установленный Deployment из 02. `kubectl set image deployment/housing api=housing:missing` меняет поле image контейнера `api` в кластере. Локальный `deployment.yaml` от этой команды не переписывается. Соседний манифест — baseline для дополнительных опытов со startupProbe/PVC, а не готовый рабочий v1 для основного сценария.

`rollout history` возвращает доступные ревизии. `rollout undo` без `--to-revision` выбирает предыдущее состояние шаблона, поэтому после дополнительных изменений выбирай явную рабочую ревизию. Результат опыта проверяется тестом задания 02: отдельной функции или теста истории отказа здесь нет.

## Технический контракт

Подмена image на `housing:missing` должна дать ошибку rollout. При `Never` ожидается ErrImageNeverPull в событиях нового Pod. После undo — снова `housing:v1`, готовность и `/predict` с первоначальной версией. Например, «rollout завершился по timeout, старый predict ещё 200» является согласованным состоянием: доступность старого и успешность нового выпуска различаются. Тест 02 проверит восстановленный результат. Историческую причину проверяешь по events непосредственно при отказе.

## Ход опыта

Используй кластер, активную среду и `MLOPS_KUBE_CONTEXT`/`MLOPS_KUBE_NAMESPACE`/`MLOPS_API_URL` из [подготовки модуля](../../README.md#подготовка-к-заданиям), в том числе в терминале pytest. Команды ниже меняют твои ресурсы. Тесты только читают подготовленное состояние.

Продолжай с рабочим Deployment v1 из задания 02. Состояние без модели из задания 01 для этого опыта не подходит.

```bash
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout history deployment/housing
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" set image deployment/housing api=housing:missing
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout status deployment/housing --timeout=60s
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" describe pods -l app=housing
```

Для намеренно отсутствующего образа `rollout status` должен завершиться ненулевым кодом. Новый Pod с imagePullPolicy Never имеет ErrImageNeverPull. Старый Ready Pod может продолжать обслуживать запросы во время неудачного RollingUpdate. При Always/IfNotPresent ожидай другую ошибку скачивания. Pending/CrashLoopBackOff/OOMKilled имеют другие причины.

```bash
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout undo deployment/housing
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollout status deployment/housing --timeout=120s
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/07-kubernetes/tasks/02-release/test_task.py -q
```

Перед последней командой заново запусти Service port-forward и укажи ожидаемую v1 model_version по README 02. Инварианты восстановления: image housing:v1, READY 1/1, predict HTTP 200 и прежняя модель. Если история содержит другие изменения, выбери явный `--to-revision` из history. Автотест 02 проверяет текущее состояние, а причину предшествующего отказа наблюдай непосредственно в describe/events. Соседний baseline можно использовать для отдельного исследования startupProbe и PVC, описанных в [теории](../../README.md#probes-конфигурация-и-хранение). Это не требуется для отката выше.

## Завершение

Останови port-forward. Перед Helm удали свои Deployment, Service и добавленный ConfigMap по манифесту задания 02:

```bash
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" delete -f modules/07-kubernetes/tasks/02-release/deployment.yaml
```

Сохрани image v1 и bundle. Кластер понадобится в следующем модуле.

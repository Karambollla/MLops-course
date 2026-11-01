# Helm: неудачный релиз и откат

Нужны завершённый 01-values, Helm 3, kubectl, kind и рабочий release housing-demo
с моделью v1. Используй task-local chart и values-dev.yaml из 01-values.
Не начинай с пустого release: atomic upgrade требует рабочую предыдущую ревизию.

```bash
export MLOPS_KUBE_CONTEXT=kind-mlops-course
export MLOPS_KUBE_NAMESPACE=default
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" history housing-demo
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" upgrade housing-demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml --set image.tag=missing --atomic --timeout 60s
echo $?
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" history housing-demo
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" get deployment housing-demo -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Иллюстрация: ненулевой exit upgrade, history содержит неуспешную попытку и
восстановленную ревизию; Deployment снова housing:v1. С прежним Service
port-forward из 01 проверь /predict: HTTP200, model_version равна модели до отказа.
Точные номера ревизий выбирай из своего history, не из примера.

Обучи реальную отличающуюся v2 через собственный housing CLI с новым seed/параметрами.
Перед заменой сохрани нужные локальные v1 артефакты; старый housing:v1 в kind
сохрани. Экспортёр читает именно output задания 01-ml/02-candidate и не запускает
обучение; `--replace` осознанно заменяет общий work/artifacts для следующей сборки.
Проверь новый bundle перед экспортом.

```bash
python -m housing.train --data work/housing.csv --output modules/01-ml/tasks/02-candidate/output --seed 43
python modules/01-ml/tasks/02-candidate/export.py --replace
docker build -t housing:v2 -f labs/kubernetes/Dockerfile.model .
kind load docker-image housing:v2 --name mlops-course
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" upgrade housing-demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml --set image.tag=v2 --wait --timeout 120s
curl --fail --max-time 10 -H 'Content-Type: application/json' --data @labs/housing/request.json http://127.0.0.1:8000/predict
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" history housing-demo
```

Иллюстрация: новая успешная ревизия и отличающаяся model_version v2. При необходимости
перезапусти port-forward после смены Pod. Выбери рабочую v1 ревизию из history:

```bash
read -r REVISION
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollback housing-demo "$REVISION" --wait --timeout 120s
curl --fail --max-time 10 -H 'Content-Type: application/json' --data @labs/housing/request.json http://127.0.0.1:8000/predict
```

Инвариант: создаётся новая ревизия release с image v1 и первоначальной model_version.
Chart version, appVersion и model_version обозначают разные вещи; `--atomic`
не откатывает внешние данные. Автоматический тест исторических переходов не
предлагается: наблюдай команды и реальные ответы, JSON-аттестация не нужна.
После блока останови forwarding и удали свой release:

```bash
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" uninstall housing-demo
```

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы иллюстрируют инварианты, а не успешный прогон. Отчёт не требуется.
[Теория](../../README.md) · [Подсказки](../../hints.md)

# Helm: values и конфигурация

## Зачем параметризовать выпуск

В Kubernetes image и конфигурация задавались в манифесте вручную. Теперь требуется менять параметры окружения, сохраняя согласованность Deployment, Service и конфигурации. Отдельная трудность — доставить изменение ConfigMap до нового процесса: существующее окружение контейнера само не обновится.

Исходное состояние — task-local chart с готовыми шаблонами Deployment/Service, но незавершёнными values и отсутствующей связью ConfigMap с rollout. `labs/helm/housing` не заменяет эту заготовку. Прочти [chart, values и release](../../README.md#chart-values-и-release), [разбор шаблона](../../README.md#как-читать-шаблон) и [конфигурацию нового Pod](../../README.md#конфигурация-и-новый-pod).

## Технический контракт

Рендер получает release name и values; создаёт согласованные Service/Deployment, ConfigMap и envFrom. Для `housing-demo` имя Service должно быть `housing-demo`, image — `housing:v1`. Смена значения существующего config key меняет SHA256 `checksum/config` в Pod template, а неизменные параметры дают тот же рендер. В шаблонах ты реализуешь эту зависимость самостоятельно. Offline-тест проверяет результат двух рендеров; реальная загрузка модели проверяется отдельными HTTP-запросами после установки.

## Реализация и проверка

Нужен Helm 3 и PyYAML (`python -m pip install PyYAML` в тестовой среде).
Редактируй **task-local** chart/ и values-dev.yaml рядом с этим README;
`labs/helm/housing` не используется в этом задании. Это исходный baseline:
добавь ConfigMap из `.Values.config`, подключи его к контейнеру через envFrom,
добавь SHA256 `checksum/config` в spec.template.metadata.annotations.
Заполни values-dev.yaml: одна реплика, image.tag=v1, непустая обычная config,
явные requests/limits с положительными значениями request <= limit.
Реализация шаблонов остаётся задачей учащегося.

```bash
helm lint modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml
helm template housing-demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/08-helm/tasks/01-values/test_task.py -q
```

Иллюстрация рендера: Service housing-demo выбирает labels Pod, Deployment с
replicas: 1, image: housing:v1, MODEL_PATH=/models/model.joblib, /live и /ready;
ConfigMap содержит твою обычную настройку, Pod использует envFrom.
Checksum — 64 hex символа и меняется при изменении значения существующего config key.
Тест рендерит два варианта через реальные helm template и временный override;
он не меняет chart/values и не подключается к Kubernetes.
После реализации ожидается 1 passed; без флага 1 skipped. С флагом отсутствие
Helm/PyYAML или незавершённые шаблоны дают failure, а не skip.

Для реальной установки нужны Docker/kind/kubectl, image housing:v1 с собственным
bundle из 07/02, загруженный в kind. Удали ручные ресурсы Kubernetes 07 перед Helm.

```bash
export MLOPS_KUBE_CONTEXT=kind-mlops-course
export MLOPS_KUBE_NAMESPACE=default
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" upgrade --install housing-demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml --wait --timeout 120s
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" status housing-demo
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" port-forward service/housing-demo 8000:8000
```

В другом терминале:

```bash
curl --fail --max-time 10 http://127.0.0.1:8000/ready
curl --fail --max-time 10 -H 'Content-Type: application/json' --data @labs/housing/request.json http://127.0.0.1:8000/predict
```

Иллюстрация: STATUS deployed, HTTP200, model_version совпадает с собственным
bundle v1. Рендер сам по себе не доказывает доступность image/модели/API.
Измени обычный config в values-dev.yaml и повтори upgrade: checksum в Pod template
меняется, создаётся новая ревизия Pod. Сохрани release для 02, останови port-forward.

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы иллюстрируют инварианты, а не успешный прогон.
[Теория](../../README.md) · [Подсказки](../../hints.md)

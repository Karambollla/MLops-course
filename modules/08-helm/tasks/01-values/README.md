# Helm: values и конфигурация

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем параметризовать выпуск

В Kubernetes image и конфигурация задавались в манифесте вручную. Теперь требуется менять параметры окружения, сохраняя согласованность Deployment, Service и конфигурации. Отдельная трудность — доставить изменение ConfigMap до нового процесса: существующее окружение контейнера само не обновится.

Исходное состояние — task-local chart с готовыми шаблонами Deployment/Service, но незавершёнными values и отсутствующей связью ConfigMap с rollout. `labs/helm/housing` не заменяет эту заготовку. Прочти [chart, values и release](../../README.md#chart-values-и-release), [разбор шаблона](../../README.md#как-читать-шаблон) и [конфигурацию нового Pod](../../README.md#конфигурация-и-новый-pod).

## Рабочие файлы и значения

Это задание на YAML и Helm templates, Python-функции реализовывать не нужно.

| Файл или параметр | Тип и формат | Откуда берётся и что редактировать | Пример |
|---|---|---|---|
| `values-dev.yaml: replicaCount` | Целое число | Override окружения. Замени `null` на одну реплику | `1` |
| `values-dev.yaml: image.tag` | Строка | Тег подготовленного в Kubernetes image с bundle | `v1` |
| `chart/values.yaml: image.repository`, `pullPolicy`, `modelPath` | Строки defaults | Сохраняются при частичном override | `housing`, `Never`, `/models/model.joblib` |
| `values-dev.yaml: resources` | Карты `requests` и `limits` с CPU/memory quantities | Явные положительные значения request ≤ limit. Формат объяснён в [ресурсах Kubernetes](../../../07-kubernetes/README.md#разобранный-манифест-и-поставка-модели) | CPU `100m`, memory `128Mi` |
| `values-dev.yaml: config` | Непустая карта строковых несекретных настроек | Собственная обычная конфигурация для ConfigMap, не token | `COURSE_MODE: development` |
| `chart/templates/deployment.yaml` | Go template, результат — Deployment YAML | Добавь envFrom на созданный ConfigMap и `spec.template.metadata.annotations.checksum/config` | SHA-256 из 64 hex символов |
| Новый шаблон ConfigMap в `chart/templates/` | Go template, результат — ConfigMap YAML | Рендерит `.Values.config` в `data`. Имя согласуй с envFrom | Имя выбирается в chart |
| Release name команды | Строка, позиционный аргумент Helm | `.Release.Name` в готовых Deployment/Service и labels | `housing-demo` |

В `Chart.yaml` лежат метаданные пакета, а не параметры модели. Менять их для выбора image не требуется. Defaults и `-f values-dev.yaml` объединяются: override tag не удаляет repository. Шаблон нужно проверять по полученному YAML, включая отступы, типы и selector. Checksum должен зависеть от config в Pod template: изменение только metadata Deployment не создаёт новую версию Pod.

## Технический контракт

Рендер получает release name и values. Создаёт согласованные Service/Deployment, ConfigMap и envFrom. Для `housing-demo` имя Service должно быть `housing-demo`, image — `housing:v1`. Смена значения существующего config key меняет SHA256 `checksum/config` в Pod template, а неизменные параметры дают тот же рендер. В шаблонах ты реализуешь эту зависимость самостоятельно. Offline-тест проверяет результат двух рендеров. Реальная загрузка модели проверяется отдельными HTTP-запросами после установки.

## Реализация и проверка

Нужен Helm 3 и PyYAML (`python -m pip install PyYAML` в тестовой среде).
Редактируй **task-local** chart/ и values-dev.yaml рядом с этим README.
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
replicas: 1, image: housing:v1, MODEL_PATH=/models/model.joblib, /live и /ready.
ConfigMap содержит твою обычную настройку, Pod использует envFrom.
Checksum — 64 hex символа и меняется при изменении значения существующего config key.
Тест рендерит два варианта через реальные helm template и временный override.
он не меняет chart/values и не подключается к Kubernetes.
После реализации ожидается 1 passed. Без флага 1 skipped. С флагом отсутствие
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

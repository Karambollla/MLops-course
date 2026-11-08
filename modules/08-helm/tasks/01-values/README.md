# Helm: values и конфигурация

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Что предстоит сделать

В Kubernetes image и конфигурация задавались в манифесте вручную. Теперь требуется менять параметры окружения, сохраняя согласованность Deployment, Service и конфигурации. Отдельная трудность — доставить изменение ConfigMap до нового процесса: существующее окружение контейнера само не обновится.

Работай в соседних [values-dev.yaml](values-dev.yaml) и [chart/](chart/Chart.yaml): заполни параметры окружения, добавь шаблон ConfigMap, его подключение и checksum в шаблон Pod. Сначала проверь два локальных рендера, затем установи release и проследи появление нового Pod после изменения конфигурации. `labs/helm/housing` не заменяет эту заготовку. Прочти [chart, values и release](../../README.md#chart-values-и-release), [разбор шаблона](../../README.md#как-читать-шаблон) и [конфигурацию нового Pod](../../README.md#конфигурация-и-новый-pod).

## Рабочие файлы и значения

Пакет из [теории модуля](../../README.md#chart-values-и-release) здесь уже содержит Deployment и Service. Values окружения пока заполнены `null`. Python-функций у задания нет. Имя устанавливаемого экземпляра выбрано `housing-demo`. Одна реплика и тег `v1` продолжают рабочее состояние предыдущего модуля. Значения ресурсов из таблицы — стартовая конфигурация маленького API, а не универсальные требования модели.

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

В [среде модуля](../../README.md#подготовка-к-заданиям) после изменений запусти:

```bash
helm lint modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml
helm template housing-demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml
MLOPS_RUN_INTEGRATION=1 python -m pytest modules/08-helm/tasks/01-values/test_task.py -q
```

В результате Service `housing-demo` должен выбирать метки Pod, Deployment — задавать одну реплику `housing:v1`, правильный `MODEL_PATH`, отдельные `/live` и `/ready` и выбранные ресурсы. Тест проверяет согласованность selector, ConfigMap/envFrom и смену 64-символьной суммы при изменении существующего config key. Для второго рендера он создаёт временный override, не меняя твои файлы и не обращаясь к кластеру. Без флага тест пропускается. С флагом отсутствие Helm/PyYAML или незавершённый шаблон дают ошибку.

Отдельно сравни два рендера без изменения values: checksum должен быть устойчивым. Автотест изменяет конфигурацию и не проверяет эту устойчивость отдельным повтором.

Для реальной установки нужны Docker/kind/kubectl, image housing:v1 с собственным bundle из 07/02, загруженный в kind. Удали ручные ресурсы Kubernetes 07 перед Helm.

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

Сравни `model_version` ответов с версией собственного bundle v1, прочитанной до запросов по [инструкции Kubernetes](../../../07-kubernetes/tasks/02-release/README.md#подготовка-и-проверка). Статус deployed вместе с HTTP 200 и ожидаемой версией подтверждает установленный результат.

Теперь измени значение собственного обычного ключа в `values-dev.yaml` и повтори upgrade. Сравни checksum в `spec.template.metadata.annotations` и имена Pod до/после: должен появиться новый экземпляр. Проверь свой ключ через `printenv` в новом контейнере, как в предыдущем модуле. Сохрани release для задания 02 и останови port-forward через `Ctrl+C`.

# Helm: неудачный релиз и откат

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Что предстоит сделать

Рабочая версия должна оставаться восстанавливаемой после двух разных событий: неудачного обновления и успешного выпуска другой модели. В первом случае изучаем atomic upgrade, во втором — явный выбор прежней ревизии. Номер revision, тег образа и model_version нельзя использовать как взаимозаменяемые обозначения.

Используй установленный `housing-demo` из задания 01, сохранённые image/bundle v1 и те же chart/values. Сначала командой upgrade выбери отсутствующий образ, затем выпусти реально переобученную модель v2 и верни прежнюю ревизию. Команды меняют установленный release. Новых шаблонов это руководство не требует. Механика разобрана в [рендере, установке и откате](../../README.md#рендер-установка-и-откат), виды версий — в [понятии release](../../README.md#chart-values-и-release).

## Технический контракт

Upgrade на отсутствующий image завершается ненулевым кодом и при успешном atomic-восстановлении возвращает v1. Затем реальное обучение создаёт другую v2. После её выпуска `/predict` должен показать новую model_version. Явный rollback на выбранную рабочую v1 revision создаёт новую запись истории и возвращает старую модель. Например, если после нескольких операций история получила номер revision 4, эта запись всё ещё может содержать image v1: номер операции не обязан совпадать с версией модели. Точные номера определяются твоей history. Готовые результаты обучения в упражнении не подставляются.

## Входы команд и наблюдаемый результат

| Вход | Тип и происхождение | Для чего нужен и пример |
|---|---|---|
| `--set image.tag=missing` | Строковый override одной операции | Намеренно выбирает отсутствующий image и не редактирует values-dev.yaml |
| `--atomic --timeout 60s` | Флаг отката и длительность ожидания Helm | Upgrade завершается ошибкой и пытается вернуть рабочую предыдущую конфигурацию |
| `--set image.tag=v2` | Тег нового самостоятельно собранного image | Новый bundle должен иметь отличающуюся `model_version` |
| `REVISION` | Номер успешной v1 revision из собственного `helm history` | Аргумент `helm rollback housing-demo "$REVISION"`, например номер из колонки REVISION |
| `labs/housing/request.json` | Файл тела POST с `instances` | Проверяет доступность API и версию модели до/после обновления |

История Helm отражает операции, поэтому `REVISION` не равен автоматически 1 или 2. Сохрани ожидаемые `model_version` v1 и v2 независимо от HTTP-ответов, читая только собственные доверенные bundle. Ошибка upgrade не подтверждает, что старый API перестал работать. После каждого перехода заново проверяй `/predict`, при замене Pod возобновляй port-forward.

## Ход опыта

Продолжай в [среде модуля](../../README.md#подготовка-к-заданиям) с рабочим release. Проверь историю и сохрани номер успешной ревизии v1: именно к нему затем вернётся явный rollback. Тег `missing` ниже выбран намеренно и не должен существовать в kind.

```bash
export MLOPS_KUBE_CONTEXT=kind-mlops-course
export MLOPS_KUBE_NAMESPACE=default
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" history housing-demo
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" upgrade housing-demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml --set image.tag=missing --atomic --timeout 60s
echo $?
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" history housing-demo
kubectl --context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" get deployment housing-demo -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Сразу после upgrade `echo $?` должен показать ненулевой код. При успешном atomic-откате history содержит неудачную попытку и восстановленную ревизию, а Deployment снова использует `housing:v1`. С прежним Service port-forward из 01 проверь /predict: HTTP 200, model_version равна модели до отказа. Точные номера ревизий выбирай из своего history, не из примера.

Для следующего перехода нужна действительно другая модель. Сохрани комплект v1 отдельно и оставь `housing:v1` в kind. Открой [ML-notebook](../../../01-ml/housing.ipynb), выбери другой seed до обучения, выполни эксперимент и экспорт финальной ячейкой с `replace=True`. Например, если v1 обучалась с seed `42`, для учебной v2 возьми `43`. Экспорт заменяет комплект в `work/artifacts/`, который читает Dockerfile. До сборки проверь, что новая `model_version` отличается от прежней. Одно переименование тега этого не обеспечивает.

Для отдельного повторного запуска без замены активного комплекта можно использовать CLI:

```bash
python -m housing.train --data work/housing.csv --output work/runs/second-release --seed 43
```

CLI сохраняет файлы только в указанный `--output`: сам по себе этот альтернативный запуск не меняет `work/artifacts/`. Для основного пути выше новый комплект экспортируется из notebook. После появления именно v2 в `work/artifacts/` собери и установи образ:

```bash
docker build -t housing:v2 -f labs/kubernetes/Dockerfile.model .
kind load docker-image housing:v2 --name mlops-course
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" upgrade housing-demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml --set image.tag=v2 --wait --timeout 120s
curl --fail --max-time 10 -H 'Content-Type: application/json' --data @labs/housing/request.json http://127.0.0.1:8000/predict
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" history housing-demo
```

Ожидаются новая успешная ревизия и `model_version`, совпадающая с прочитанной из bundle v2. При необходимости перезапусти port-forward после смены Pod. Выбери рабочую v1 ревизию из history. Команда `read` ждёт в терминале её номер и сохраняет его в `REVISION`:

```bash
read -r REVISION
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" rollback housing-demo "$REVISION" --wait --timeout 120s
curl --fail --max-time 10 -H 'Content-Type: application/json' --data @labs/housing/request.json http://127.0.0.1:8000/predict
```

После rollback появляется новая ревизия release с `housing:v1`. Проверь `/ready` и `/predict`: версия должна совпасть с сохранённой v1, а не с последним ответом v2. Chart version, appVersion и model_version обозначают разные вещи. `--atomic` не откатывает внешние данные. Автоматический тест исторических переходов не предлагается: наблюдай команды и реальные ответы. После блока останови forwarding и удали свой release:

```bash
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" uninstall housing-demo
```

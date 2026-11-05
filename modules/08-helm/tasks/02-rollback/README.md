# Helm: неудачный релиз и откат

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем проверять историю release

Рабочая версия должна оставаться восстанавливаемой после двух разных событий: неудачного обновления и успешного выпуска другой модели. В первом случае изучаем atomic upgrade, во втором — явный выбор прежней ревизии. Номер revision, тег образа и model_version нельзя использовать как взаимозаменяемые обозначения.

На входе — установленный `housing-demo` из задания 01, сохранённые v1 image/bundle и готовые chart/values. Новых шаблонов это руководство не требует. Механика разобрана в [рендере, установке и откате](../../README.md#рендер-установка-и-откат), виды версий — в [понятии release](../../README.md#chart-values-и-release).

## Технический контракт

Upgrade на отсутствующий image завершается ненулевым кодом и при успешном atomic-восстановлении возвращает v1. Затем реальное обучение создаёт другую v2. После её выпуска `/predict` должен показать новую model_version. Явный rollback на выбранную рабочую v1 revision создаёт новую запись истории и возвращает старую модель. Например, revision 4 может содержать image v1: номер операции не обязан совпадать с версией модели. Точные номера определяются твоей history. Готовые результаты обучения в упражнении не подставляются.

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
восстановленную ревизию. Deployment снова housing:v1. С прежним Service
port-forward из 01 проверь /predict: HTTP200, model_version равна модели до отказа.
Точные номера ревизий выбирай из своего history, не из примера.

Обучи реальную отличающуюся v2 через собственный housing CLI с новым seed/параметрами.
Перед заменой сохрани нужные локальные v1 артефакты. Старый housing:v1 в kind
сохрани. Для второй версии открой ML-notebook, задай другой seed до обучения,
выполни эксперимент и финальную ячейку с `replace=True`. Это заменяет комплект
в `work/artifacts/`. Предыдущий файл оставь доступным для отката.

Для отдельного повторного запуска без замены активного комплекта можно использовать CLI:

```bash
python -m housing.train --data work/housing.csv --output work/runs/second-release --seed 43
```

После сохранения v2 в `work/artifacts/` собери и установи её:

```bash
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
Chart version, appVersion и model_version обозначают разные вещи. `--atomic`
не откатывает внешние данные. Автоматический тест исторических переходов не
предлагается: наблюдай команды и реальные ответы.
После блока останови forwarding и удали свой release:

```bash
helm --kube-context "$MLOPS_KUBE_CONTEXT" --namespace "$MLOPS_KUBE_NAMESPACE" uninstall housing-demo
```

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы иллюстрируют инварианты, а не успешный прогон.

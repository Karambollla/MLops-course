# Практика: Helm: воспроизводимые релизы

[Теория](README.md) · [Подсказки](hints.md)

## Подготовка и установка

Сначала удали ручной Deployment/Service модуля 07. Image housing:v1 должен быть загружен в kind.

```bash
helm lint labs/helm/housing
helm template housing labs/helm/housing --set image.tag=v1
helm --kube-context kind-mlops-course upgrade --install housing labs/helm/housing --set image.tag=v1 --wait --timeout 120s
```

Проверь release status и `/predict` через port-forward. Не используй базовый image `course` для успешной установки с readiness: в нём нет модели.

## Задание 1. Values

Создай values-dev.yaml с одной репликой и явными ресурсами. Добавь обычную конфигурацию через ConfigMap и checksum-аннотацию. Сравни рендер до/после изменения параметра. Артефакт: chart, values и маленький diff ожидаемого YAML.

## Задание 2. Неудачный релиз

```bash
helm --kube-context kind-mlops-course upgrade housing labs/helm/housing --set image.tag=missing --atomic --timeout 60s
helm --kube-context kind-mlops-course history housing
```

Первая команда должна завершиться ошибкой и восстановить рабочую поставку. Подтверди прогноз и версию модели. Затем подготовь другой реальный bundle/image v2, выпусти и верни предыдущую ревизию через `helm rollback housing REVISION --wait` с явным kube-context.

## Критерии готовности

- [ ] Chart проходит lint и даёт читаемый рендер.
- [ ] Поставку можно повторить из сохранённых values.
- [ ] После неудачного upgrade доступны прогнозы прежней модели.
- [ ] Объяснены границы --atomic и различия chart/app/model version.

## Завершение

`helm --kube-context kind-mlops-course uninstall housing`. Останови port-forward; при завершении Kubernetes-блока удали только кластер mlops-course.

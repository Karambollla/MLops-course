# Практика: Kubernetes: выкладка и диагностика

[Теория](README.md) · [Подсказки](hints.md)

## Задание 1. Живой, но неготовый API

Создай кластер по SETUP, собери базовый image:

```bash
docker build -t housing:course labs/housing
kind load docker-image housing:course --name mlops-course
kubectl --context kind-mlops-course apply -f labs/kubernetes/deployment.yaml
kubectl --context kind-mlops-course get pods
```

Ожидается Running с 0/1 Ready без модели. Изучи `describe pod` и readiness events. Доступ к Pod для диагностики можно получить через `kubectl port-forward deployment/housing 8000:8000`; это не проверка маршрутизации Service.

## Задание 2. Рабочий выпуск

После обучения:

```bash
docker build -t housing:v1 -f labs/kubernetes/Dockerfile.model .
kind load docker-image housing:v1 --name mlops-course
kubectl --context kind-mlops-course set image deployment/housing api=housing:v1
kubectl --context kind-mlops-course rollout status deployment/housing --timeout=120s
kubectl --context kind-mlops-course port-forward service/housing 8000:8000
```

В другом терминале отправь request.json. Ожидаются Ready 1/1, HTTP 200 и правильная model_version. Добавь ConfigMap для непустой обычной настройки, затем объясни необходимость rollout при изменении env.

## Задание 3. Сбой

Смени image на несуществующий локальный тег `housing:missing`, изучи events и верни `housing:v1` через rollout undo. Отдельно объясни, как выглядел бы OOMKilled; не нужно намеренно расходовать всю RAM ноутбука. Дополнительно добавь startupProbe и исследуй PVC в kind.

## Критерии готовности

- [ ] Различаешь Pending, CrashLoopBackOff и неготовый Running.
- [ ] Модель и код версионированы вместе; восстановлена рабочая версия.
- [ ] Requests/limits объяснены и не превышают бюджет стенда.

## Завершение

Останови port-forward. Удали ресурсы `kubectl --context kind-mlops-course delete -f labs/kubernetes/deployment.yaml` перед Helm. Кластер оставь для следующего модуля.

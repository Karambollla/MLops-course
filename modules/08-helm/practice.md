# Практика: Helm: воспроизводимые релизы

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Values](tasks/01-values/README.md) | [Заготовка](tasks/01-values/report.json) · [тесты](tasks/01-values/test_task.py) | cpu |
| [Неудачный релиз](tasks/02-rollback/README.md) | [Заготовка](tasks/02-rollback/report.json) · [тесты](tasks/02-rollback/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=08-helm/01-values
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка и установка

Сначала удали ручной Deployment/Service модуля 07. Image housing:v1 должен быть загружен в kind.

```bash
helm lint labs/helm/housing
helm template housing labs/helm/housing --set image.tag=v1
helm --kube-context kind-mlops-course upgrade --install housing labs/helm/housing --set image.tag=v1 --wait --timeout 120s
```

Проверь release status и `/predict` через port-forward. Не используй базовый image `course` для успешной установки с readiness: в нём нет модели.

## Завершение

`helm --kube-context kind-mlops-course uninstall housing`. Останови port-forward; при завершении Kubernetes-блока удали только кластер mlops-course.

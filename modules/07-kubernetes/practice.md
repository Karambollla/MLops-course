# Практика: Kubernetes: выкладка и диагностика

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Живой, но неготовый API](tasks/01-unready/README.md) | [Заготовка](tasks/01-unready/report.json) · [тесты](tasks/01-unready/test_task.py) | cpu |
| [Рабочий выпуск](tasks/02-release/README.md) | [Заготовка](tasks/02-release/report.json) · [тесты](tasks/02-release/test_task.py) | cpu |
| [Сбой](tasks/03-failure/README.md) | [Заготовка](tasks/03-failure/report.json) · [тесты](tasks/03-failure/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=07-kubernetes/01-unready
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Завершение

Останови port-forward. Удали ресурсы `kubectl --context kind-mlops-course delete -f labs/kubernetes/deployment.yaml` перед Helm. Кластер оставь для следующего модуля.

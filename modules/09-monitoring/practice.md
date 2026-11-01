# Практика: Prometheus, Grafana и качество модели

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Нагрузка и dashboard](tasks/01-load-dashboard/README.md) | [Старт](tasks/01-load-dashboard/solution.py) · [Тесты функций](tasks/01-load-dashboard/test_task.py) | cpu |
| [Отказ](tasks/02-outage/README.md) | [Старт](tasks/02-outage/rules.yaml) · [Проверка стенда](tasks/02-outage/test_task.py) | cpu |
| [Качество и drift](tasks/03-quality-drift/README.md) | [Старт](tasks/03-quality-drift/solution.py) · [Тесты функций](tasks/03-quality-drift/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=09-monitoring/01-load-dashboard
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Функции проверяются прямо на фиксированных входах. Live-проверки читают существующий стенд только с MLOPS_RUN_INTEGRATION=1; guides не требуют отдельной сдачи.

## Подготовка

Останови API другого Compose-стенда и kind при недостатке ресурсов.

```bash
docker compose -f labs/monitoring/compose.yaml up -d --build
```

Prometheus: 9090; Grafana: 3000, локальный вход student / local-course-only. Dashboard Housing course и datasource создаются автоматически. Без модели API жив, но predict даёт 503.

## Завершение

`docker compose -f labs/monitoring/compose.yaml down`. Перед удалением volume выгрузи свой dashboard JSON.

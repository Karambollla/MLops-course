# Kubernetes: живой, но неготовый API

Зависит от Docker, kind и образа модуля 03. Объясни разницу процесса, готовности и маршрутизации Service.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов. Нужен Docker daemon, kubectl и kind; Python Kubernetes SDK не требуется.

Создай kind mlops-course по SETUP. `docker build -t housing:course -f labs/housing/Dockerfile .`; `kind load docker-image housing:course --name mlops-course`. Редактируй task-local deployment.yaml при необходимости, примени `kubectl --context kind-mlops-course apply -f modules/07-kubernetes/tasks/01-unready/deployment.yaml`. Собери get pods, describe/events, endpoints и HTTP ответы. `kubectl --context kind-mlops-course port-forward deployment/housing 8000:8000` помогает диагностике Pod, но не доказывает маршрутизацию Service. Не подменяй readiness на /live.

Проверка выбранного задания:

```bash
make task TASK=07-kubernetes/01-unready
python scripts/run_task.py run 07-kubernetes/01-unready -- --report modules/07-kubernetes/tasks/01-unready/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`validate_report(report) -> {"diagnosis": "model_not_ready", "service_routes_traffic": False}`. Для сценария fixture: Running, ready=false, /live=200, /ready=503, endpoints=0, image housing:course, model_version=null, разные probe paths /live и /ready и событие readiness. Другие сочетания отклоняй.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

Останови port-forward; оставь Deployment для следующего задания. Перед Helm удали ручные ресурсы тем же task-local манифестом.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

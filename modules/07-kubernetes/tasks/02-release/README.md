# Kubernetes: рабочий выпуск

Зависит от своего bundle из 01–03 и 07/01. Версионируй код и модель вместе.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов.

`docker build -t housing:v1 -f labs/kubernetes/Dockerfile.model .`; `kind load docker-image housing:v1 --name mlops-course`. В task-local deployment.yaml поменяй image, добавь непустой ConfigMap и envFrom/env; примени и дождись rollout (120s). Port-forward **service/housing** и отправь labs/housing/request.json. Сохрани настоящий model_version из ответа и bundle manifest, digest и endpoints. Измени обычную настройку ConfigMap, покажи старое значение env до rollout и новое после него; объясни requests/limits.

Проверка выбранного задания:

```bash
make task TASK=07-kubernetes/02-release
python scripts/run_task.py run 07-kubernetes/02-release -- --report modules/07-kubernetes/tasks/02-release/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`validate_report(report) -> {"model_version": str, "ready": True}`. Непустой release_id, immutable housing:v1 и digest sha256/64 hex, desired=ready>=1, endpoints>=1, HTTP200 и непустая model_version == expected_model_version. configmap непустой, совпадает с pod_env; config_revision == pod_config_revision; 0 < memory_request_mib <= memory_limit_mib <= 1024.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

Останови port-forward, сохрани v1 для отката. Перед Helm удали Deployment/Service/свой ConfigMap.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

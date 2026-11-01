# Мониторинг: отказ и восстановление

Зависит от 09/01. Firing в Prometheus не доказывает внешнюю доставку уведомления.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов.

Зафиксируй baseline, `docker compose -f labs/monitoring/compose.yaml stop api`; дождись pending и Firing HousingTargetDown, сохрани реальные timestamps. `docker compose -f labs/monitoring/compose.yaml start api`; дождись снятия alert и успешного predict. Повтори с живым API без модели: up остаётся 1, готовность/predict 503. Добавь соответствующее правило в task-local rules.yaml; заполни runbook. Объясни причину/следствие, for interval и доступные действия оператора.

Проверка выбранного задания:

```bash
make task TASK=09-monitoring/02-outage
python scripts/run_task.py run 09-monitoring/02-outage -- --report modules/09-monitoring/tasks/02-outage/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`validate_report(report) -> {"detection_seconds": number, "recovery_seconds": number}`. stopped<=pending<firing<=restarted<resolved и firing-pending>=for_seconds>0; alert HousingTargetDown и полный цикл states fixture; down_up=0, recovered_up=1. no_model строго up=1/ready=503/predict=503, дополнительное правило как fixture. runbook содержит непустые symptom/check/recovery/success.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

Верни bundle и рабочий API. Экспортируй отчёт, затем compose down; тесты сами stop/start не выполняют.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

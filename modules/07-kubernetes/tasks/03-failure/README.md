# Kubernetes: сбой и восстановление

Зависит от рабочего v1 в 07/02. Не нужно искусственно исчерпывать RAM.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов.

Смени Deployment image на housing:missing; сохрани events/describe. При Never ожидается ErrImageNeverPull, при политике скачивания — ImagePullBackOff. `kubectl --context kind-mlops-course rollout undo deployment/housing`; дождись готовности, проверь image и model_version через predict. Вручную объясни Pending, crash loop, OOMKilled и почему рестарт не устраняет превышение memory limit. Дополнительно: добавь startupProbe в task-local манифест и исследуй PVC kind, не утверждая, что диск Pod постоянный.

Проверка выбранного задания:

```bash
make task TASK=07-kubernetes/03-failure
python scripts/run_task.py run 07-kubernetes/03-failure -- --report modules/07-kubernetes/tasks/03-failure/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`validate_report(report) -> {"restored": True, "image_failure": str}`. housing:missing + Never требует ErrImageNeverPull (для IfNotPresent/Always — ImagePullBackOff); failed_ready=false. Откат housing:v1, ready=true, HTTP200 и совпадение непустых rollback_model/expected_model. diagnoses должен различать четыре причины как fixture.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

Удали ручные ресурсы Kubernetes перед Helm, останови port-forward. Кластер mlops-course оставь следующему модулю.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

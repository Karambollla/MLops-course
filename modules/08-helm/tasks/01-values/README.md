# Helm: values и конфигурация

Зависит от загруженного housing:v1 и удаления ручного Deployment/Service 07. Рендер не заменяет smoke-test.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов. Дополнительно Helm 3, kubectl, kind. Chart скопирован как исходный baseline, учебные дополнения ещё отсутствуют.

В task-local chart/ добавь ConfigMap и checksum содержимого ConfigMap в Pod template. Заполни values-dev.yaml: одна реплика, явные ресурсы, обычная настройка без secret. `helm lint modules/08-helm/tasks/01-values/chart`; `helm template housing-demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml`. Сохрани рендер до/после и небольшой diff. Установи через helm --kube-context kind-mlops-course upgrade --install с --wait --timeout 120s. Проверь release status и predict через service/housing-demo. Покажи, что checksum реально меняется при изменении настройки.

Проверка выбранного задания:

```bash
make task TASK=08-helm/01-values
python scripts/run_task.py run 08-helm/01-values -- --report modules/08-helm/tasks/01-values/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`validate_report(report) -> {"rollout_required": True, "service_name": str}`. Имена service/release совпадают; housing:v1, replicas=1, 0<request<=limit<=1024. Непустые config_before/after различаются; sha256 checksums (64 hex) различаются и находятся в spec.template.metadata.annotations. render_changed_fields содержит оба пути fixture; готовность, HTTP200 и совпадение непустых model IDs обязательны.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

Сохрани release для следующего упражнения, останови port-forward; после блока `helm --kube-context kind-mlops-course uninstall housing-demo`.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

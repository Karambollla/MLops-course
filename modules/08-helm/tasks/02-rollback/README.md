# Helm: неудачный релиз и rollback

Зависит от 08/01. Требуются два реальных разных bundle/image, а не переименование одного mutable tag.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов.

Выполни `helm --kube-context kind-mlops-course upgrade housing-demo modules/08-helm/tasks/01-values/chart --set image.tag=missing --atomic --timeout 60s` с сохранёнными values. Сохрани ненулевой exit, history и прежнюю модель в predict. Обучи/собери реальный v2, загрузи image в kind, выпусти и проверь новую модель. Выбери из history конкретную рабочую REVISION и `helm --kube-context kind-mlops-course rollback housing-demo REVISION --wait`. Убедись в старой версии модели. Вручную объясни chart version/appVersion/model version и почему --atomic не откатывает внешние данные.

Проверка выбранного задания:

```bash
make task TASK=08-helm/02-rollback
python scripts/run_task.py run 08-helm/02-rollback -- --report modules/08-helm/tasks/02-rollback/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`validate_report(report) -> {"atomic_restored": True, "manual_restored": True}`. Неуспешный upgrade_exit !=0 с housing:missing и atomic=true; строго возрастающие before/failed/restored/v2/manual ревизии, target=before_revision, model до/после atomic/manual одинаковая непустая, v2 отличается, все три predict_statuses=200. history_statuses соответствует fixture; external_state_rolled_back=false.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

`helm --kube-context kind-mlops-course uninstall housing-demo`; останови port-forward. После Kubernetes-блока удали только kind кластер mlops-course.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

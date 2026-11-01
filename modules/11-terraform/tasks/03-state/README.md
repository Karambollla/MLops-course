# Terraform: state, import и backend

Зависит от собственного ресурса/state 11/01–02. JSON state не редактируй и не выкладывай в Git.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов.

Из каталога 11/01 выполни terraform state list и terraform show -json; сохрани только разрешённые IDs/адреса в report.json. Сверь ID контейнера с docker inspect. В design.md объясни потерю связи после потери state, конфликт имени при новом create и import по точному resource address/ID. Не нужно действительно терять state: разбор сценария должен быть явно помечен как прогноз. Раздели HCL, state и .terraform.lock.hcl. Опиши remote backend, locking, контроль доступа, secrets и почему sensitive не шифрует JSON. Вручную оцени осмысленность аргументов и процедуру восстановления.

Проверка выбранного задания:

```bash
make task TASK=11-terraform/03-state
python scripts/run_task.py run 11-terraform/03-state -- --report modules/11-terraform/tasks/03-state/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

Grader сверяет оба resource addresses, state_container_id == observed_container_id == import_id, import_address docker_container.web, versions, lost_state_plan_actions=[create], запрет state в Git, secrets=true/sensitive_encrypts=false, remote/locking/access_control=true и три назначения roles fixture. Результат {"bindings_consistent": True, "team_backend_ready": True}.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

В каталоге 11/01 с прежним Docker endpoint выполни terraform destroy и проверь удаление только учебного контейнера. Удали plan, не коммить state.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

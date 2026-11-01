# Terraform: повторный plan и изменение порта

Зависит от Docker daemon, Terraform и локального Nginx. Облачные аккаунты не нужны.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов. Terraform 1.11.4, provider kreuzwerker/docker 3.0.2; init требует сеть или подготовленный plugin cache.

Работай в task-local main.tf: добавь переменную host_port вместо 8099 в resource/output; сохраняй pin 1.11.4/provider3.0.2 и network_mode=bridge. Получи endpoint через `docker context inspect --format '{{.Endpoints.docker.Host}}'` и задай TF_VAR_docker_host. В каталоге задания выполни terraform init/fmt -check/validate/plan -out=course.tfplan/apply course.tfplan. Проверь HTTP8099. Повтори plan, экспортируй `terraform show -json course.tfplan` в JSON и помести настоящий resource_changes в report. Измени только host_port, сохрани новый plan, объясни update или replacement по реальным actions (не по текстовой догадке). Не скрывай drift через ignore_changes.

Проверка выбранного задания:

```bash
make task TASK=11-terraform/01-repeat
python scripts/run_task.py run 11-terraform/01-repeat -- --report modules/11-terraform/tasks/01-repeat/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

Офлайн grader проверяет Terraform 1.11.4/provider 3.0.2/network bridge, HTTP200/endpoint, неизменный Docker host, repeat_plan.resource_changes только no-op; port_plan для docker_container.web содержит update или delete+create и explanation совпадает с действием. old_port != new_port в диапазоне 1024..65535. Результат {"idempotent": True, "port_action": "replacement"|"update"}.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

В **том же task-local каталоге** и с тем же Docker endpoint выполни terraform destroy. Убедись, что удалён только mlops-course-terraform; удали saved plan после экспорта, state не коммить.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

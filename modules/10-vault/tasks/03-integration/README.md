# Vault: интеграционное решение

Архитектурный отчёт зависит от 10/01–02 и понимания Kubernetes identity. Не добавляй Vault к обычному локальному файлу ради демонстрации.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов.

Выбери реальное место потребления секрета: приватный bundle или внешняя зависимость. В report.template.json опиши Kubernetes auth: service account JWT → Vault role с namespace/SA binding → ограниченный token. В task-local design.md изложи secret zero, TTL/renew/revoke, поведение кеша и ротации, startup-only vs per-request. Сравни KV static versioned value с dynamic leased credential. Вручную оцени доверие к identity, отсутствие root в Pod и осмысленность выбранной зависимости. Автоматическая проверка не оценивает качество архитектурных аргументов.

Проверка выбранного задания:

```bash
make task TASK=10-vault/03-integration
python scripts/run_task.py run 10-vault/03-integration -- --report modules/10-vault/tasks/03-integration/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`validate_report(report) -> {"requires_vault": bool}`. use_case local_read_only требует secret_needed=false, auth_method=none. private_artifact/external_dependency требует secret_needed=true, auth_method=kubernetes, непустые namespace/service_account/role, service_account_jwt как secret_zero, минимальную read policy secret/data/housing, TTL>0, on_expiry=unready|stop и rotation=reload_on_renewal|restart. Всегда pod_uses_root=false и kv_is_dynamic=false.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

Никакого production deployment не требуется; очисти dev Vault и переменные токенов.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

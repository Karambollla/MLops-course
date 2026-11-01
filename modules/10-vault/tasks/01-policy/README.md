# Vault: минимальные права

Ограниченный application token не должен наследовать root. Зависит от dev Vault, HTTP и переменных окружения.

## Что редактировать

Реализуй предметные TODO в `solution.py`: входы и ожидаемые результаты перечислены ниже в разделе «Контракт и проверка» и в `test_task.py`. После практического опыта заполни `report.json` собственными наблюдениями по `report.template.json`.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов. urllib входит в stdlib; токен не хранится в конфиге.

`docker compose -f labs/vault/compose.yaml up -d` (сохрани лимит **1g**, 256Mi вызывает OOM при старте ARM64). Внутри контейнера с учебным course-root запиши secret/housing artifact_key. Заполни task-local policy.hcl: единственный API path secret/data/housing и read. Скопируй policy в контейнер, vault policy write housing и vault token create -policy=housing -ttl=60s -renewable=false. Экспортируй выданный application VAULT_TOKEN и VAULT_ADDR. Выполни CLI, отдельно соседний GET и write: оба должны вернуть 403. Сохрани только коды/имена полей, не значения. Для проверки report вызови validate_report из Python; основной CLI читает реальный Vault.

Проверка выбранного задания:

```bash
make task TASK=10-vault/01-policy
python scripts/run_task.py run 10-vault/01-policy --
```

CLI без аргументов выполняет реальную операцию; параметры берёт из окружения, как описано выше.

## Контракт и проверка

`inspect_payload(payload) -> {"field_present": True}` читает KV v2 data.data.artifact_key, не возвращая значения; отсутствующее/пустое поле — ValueError. `validate_report(report) -> {"least_privilege": True}` требует path/field fixture, read200/neighbor403/write403, capabilities только read, token_role application, field_present true и secret_logged false. `main()` читает VAULT_ADDR (default <http://127.0.0.1:8200)/VAULT_TOKEN>, выполняет GET /v1/secret/data/housing с timeout=5 и печатает только inspect_payload.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

`unset VAULT_TOKEN`; после следующих заданий compose down. Dev state исчезает после остановки.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

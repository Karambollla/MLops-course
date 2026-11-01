# Минимальные права

## Зачем проверять минимальный доступ

Клиенту нужен один ключ чтения артефакта, а не право изменять все секреты. Успешный запрос с root не проверяет это ограничение. Поэтому здесь одновременно проверяются разрешённое чтение, отказ соседнему пути и отсутствие значения секрета в результате программы.

Уже есть локальный dev Vault и HTTP-обвязка в `solution.py`; настройка стенда описана в практике. Ты реализуешь проверку payload и ограничиваешь task-local policy. Различие участников объясняется в [аутентификации и авторизации](../../README.md#кто-удостоверяет-клиента-и-кто-разрешает-чтение), структура — в [KV v2](../../README.md#kv-v2-путь-политика-и-форма-ответа).

## Контракт данных и прав

Вход `inspect_payload` — распарсенный JSON с полем `data.data.artifact_key`; выход — только `{"field_present": true}`. Например, `{"data":{"data":{"artifact_key":"fake-demo"}}}` подтверждает наличие поля, но строка `fake-demo` не появляется в результате. Отсутствующее поле или структура дают ValueError. Policy разрешает read только `secret/data/housing`; приложение использует отдельный ограниченный token. Тесты проверяют чистую функцию, реальный GET выполняется тобой после подготовки Vault.

## Реализация и проверка

Реализуй `inspect_payload(payload)`: из Vault KV v2 ответа проверь наличие artifact_key и верни только `{"field_present": true}`. Отсутствующая структура/поле — ValueError. Значение секрета никогда не возвращай и не печатай. `policy.hcl` ограничь read на `secret/data/housing`.

```bash
make task TASK=10-vault/01-policy
```

Подготовь Vault и ограниченный application token по [практике](../../practice.md). Не запускай клиент с root token. Следующие команды печатают только HTTP-код:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/housing"
curl -s -o /dev/null -w '%{http_code}\n' -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/neighbor"
python scripts/run_task.py run 10-vault/01-policy
```

Ожидаются 200, 403 и field_present=true. Write запрещён политикой; проверяй capabilities при ручной настройке, не записывай секреты ради теста. Ошибка 403 отличается от timeout. Не сохраняй токены в файлы проекта. После практики unset VAULT_TOKEN и останови dev Vault.

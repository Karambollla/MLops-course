# Минимальные права

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

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

# Минимальные права: Python SDK Vault

[Теория](../../README.md) · [Практика](../../practice.md) · [Подсказки](../../hints.md)

Клиент читает один ключ закрытого артефакта. Администратор готовит dev Vault, секрет `secret/housing` и policy; приложение использует отдельный ограниченный token. Успех с root не проверяет минимальные права.

Реализуй `inspect_payload(payload)` и `read_secret(client,path="housing",mount_point="secret")`. Первая функция проверяет `data.data.artifact_key`: возвращает только `{"field_present":true}`, при неверной структуре или отсутствии поля вызывает ValueError. Вторая вызывает `client.secrets.kv.v2.read_secret_version`, передаёт логический путь `housing` и mount `secret`, затем использует первую функцию. В HTTP SDK сам добавляет `/v1/secret/data/`. Не возвращай исходный payload, значение ключа, token и текст ошибок; не печатай их. Ошибки SDK `hvac.exceptions.Forbidden` и `requests.exceptions.Timeout` передавай вызывающему коду без повторов: CLI отображает безопасный исход и завершает процесс с ошибкой.

`solution.py` уже создаёт настоящий `hvac.Client` из env с таймаутом. Заполни task-local `policy.hcl`: разрешено только чтение `secret/data/housing`, без wildcard. Подготовка стенда и установка `hvac==2.3.0` описаны в практике.

```bash
make task TASK=10-vault/01-policy
MLOPS_RUN_SDK=1 make task TASK=10-vault/01-policy
python scripts/run_task.py run 10-vault/01-policy
```

CLI читает `VAULT_ADDR`/`VAULT_TOKEN`, принимает `--address`, `--path`, `--mount`, `--timeout`. После реализации ожидается только field_present=true. SDK-тест проходит через настоящий hvac KV2 и подменяет лишь transport без сетевого сервиса. Без SDK базовая коллекция работает, SDK-тест пропущен; незаполненные функции дают NotImplementedError.

На уже подготовленном Vault с ограниченным application token:

```bash
MLOPS_RUN_INTEGRATION=1 make task TASK=10-vault/01-policy
curl -s -o /dev/null -w '%{http_code}\n' -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/housing"
curl -s -o /dev/null -w '%{http_code}\n' -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/neighbor"
```

Live-тест вызывает именно твою `read_secret`: разрешённый путь даёт field_present=true, соседний — Forbidden/403. Он ничего не создаёт и не меняет; `VAULT_DENIED_PATH` позволяет указать другой заведомо запрещённый логический путь. Отрицательная проверка ловит ошибочное использование root. Отдельные curl probes сохранены для диагностики и печатают только коды 200/403. Закончи `unset VAULT_TOKEN`, затем `docker compose -f labs/vault/compose.yaml down`.

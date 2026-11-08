# Прочитать один ключ через Vault SDK

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

Загрузчику модели нужно прочитать ключ закрытого хранилища. Он не должен получать право читать соседние значения или записывать новые. В этом задании ты ограничишь доступ одним путём и реализуешь чтение через `hvac`. Учебная функция проверяет наличие ключа. Скачивания модели здесь нет.

Работа выполняется в двух соседних файлах: [policy.hcl](policy.hcl) задаёт права на сервере, [solution.py](solution.py) — поведение клиента. CLI создания `hvac.Client` и обработки ошибок уже готов. Сначала напиши функции и policy, затем выдай краткоживущий token: иначе он может истечь ещё до первого запуска.

## Шаг 1. Ограничить серверное разрешение

Один и тот же секрет передаётся интерфейсам по-разному. Соответствие разобрано в [главе о KV v2](../../README.md#kv-v2-путь-политика-и-форма-ответа). Для задания логическое имя — `housing`, mount — `secret`. В policy нужен путь API `secret/data/housing` и единственная capability `read`.

Заполни `policy.hcl`. Правило должно разрешать только это чтение: без wildcard и дополнительных путей. Проверка имеет две стороны: нужное значение читается, соседнее `neighbor` вызывает отказ. Root token обойдёт это ограничение, поэтому клиент упражнения получит отдельный token.

## Шаг 2. Проверить ответ и вызвать SDK

```python
def inspect_payload(payload):
    ...

def read_secret(client, path="housing", mount_point="secret") -> dict:
    ...
```

| Вход | Формат и источник | Что с ним сделать |
|---|---|---|
| `payload` | Ответ KV v2: `{"data": {"data": {"artifact_key": "example-key"}, "metadata": {"version": 1}}}` | Убедиться, что вложенные уровни — словари и внутренний содержит `artifact_key` |
| `client` | Настроенный `hvac.Client`. В быстрых тестах объект с тем же интерфейсом | Использовать `client.secrets.kv.v2.read_secret_version` |
| `path` | Логическое имя, default `"housing"` | Передать в именованный аргумент `path` SDK. Не добавлять `data/` |
| `mount_point` | Имя engine, default `"secret"` | Передать отдельно в именованный аргумент `mount_point` SDK |

`inspect_payload` возвращает ровно `{"field_present": True}`. Пустая строка в поле тоже означает, что ключ присутствует: проверяется структура, а не пригодность значения. Отсутствие поля, словаря или неверная вложенность вызывают `ValueError`.

`read_secret` делает один SDK-вызов, передаёт ответ в `inspect_payload` и возвращает её безопасный результат. Ошибки SDK должны дойти до вызывающего кода без retry. Значение, полный payload и token нельзя печатать или возвращать. Уже подготовленный CLI преобразует `Forbidden` в `access_denied`, `Timeout` — в `network_timeout`, прочий `VaultError` — в `vault_error`, с кодом завершения 1.

Проверь реализацию без сервера:

```bash
make task TASK=10-vault/01-policy
MLOPS_RUN_SDK=1 make task TASK=10-vault/01-policy
```

Первая команда использует подменённый клиент и фиксированные ответы. Для второй нужен `hvac` из [подготовки](../../README.md#подготовка-к-заданиям): тест проходит настоящий путь KV v2 SDK до подменённого HTTP-транспорта и проверяет URL `/v1/secret/data/housing`. Без флага SDK-тест пропускается. До реализации функций ожидается `NotImplementedError`.

## Подготовить данные и ограниченный token

Запусти dev Vault по [инструкции модуля](../../README.md#подготовка-к-заданиям). Дальше администратор выполняет три разных действия: сохраняет вымышленное значение, загружает твою policy под именем `housing`, выдаёт клиенту token с этой policy. Имя policy — ссылка из token на набор прав. Это не имя секрета, хотя для практики строки совпадают.

Из корня курса:

```bash
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault kv put secret/housing artifact_key=local-demo-value
docker compose -f labs/vault/compose.yaml cp modules/10-vault/tasks/01-policy/policy.hcl vault:/tmp/policy.hcl
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault policy write housing /tmp/policy.hcl
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault token create -policy=housing -ttl=60s -renewable=false
```

Последняя команда показывает временный token. Это доступ на 60 секунд без продления. Скопируй его для текущего shell, не сохраняй полный вывод в проект. При истечении выпусти новый token той же командой. Прочитай ограниченный token без эха:

```bash
read -s VAULT_TOKEN
export VAULT_TOKEN
export VAULT_ADDR=http://127.0.0.1:8200
```

## Проверить реальное чтение

```bash
python modules/10-vault/tasks/01-policy/solution.py --path housing --mount secret
MLOPS_RUN_INTEGRATION=1 make task TASK=10-vault/01-policy
```

CLI должен напечатать только `{"field_present": true}`. Live-тест вызывает твою `read_secret` для `housing`, затем для запрещённого `neighbor`: ожидает безопасный результат и `Forbidden`. Он не создаёт policy или данные. `VAULT_DENIED_PATH` позволяет выбрать другое заведомо запрещённое логическое имя.

| Параметр CLI | Откуда берётся | Значение по умолчанию |
|---|---|---|
| `--address` | Переопределяет `VAULT_ADDR` | `http://127.0.0.1:8200`, если env отсутствует |
| `VAULT_TOKEN` | Ограниченный token текущего shell | Обязателен, CLI-флага для него нет |
| `--path`, `--mount` | Логическое имя и mount | `housing`, `secret` |
| `--timeout` | Положительное время ожидания в секундах | `5` |

Для диагностики можно проверить только HTTP-коды, не выводя тело ответа:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/housing"
curl -s -o /dev/null -w '%{http_code}\n' -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/neighbor"
```

Ожидаются 200 и 403. Два успешных чтения означают слишком широкие права или использование root. Два отказа могут означать истёкший token. Проверь время и policy.

## Завершение

Для следующего задания оставь dev Vault, значение и policy. Текущий ограниченный token можно удалить из окружения командой `unset VAULT_TOKEN`: следующий опыт использует новые временные token. Остановка и полная очистка — в [конце модуля](../../README.md#проверки-и-завершение).

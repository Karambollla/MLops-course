# Минимальные права: Python SDK Vault

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Подготовка и рабочие файлы

Общая [подготовка dev Vault](../../README.md#подготовка-к-заданиям) включает основной Python, установку `hvac==2.3.0`, создание секрета и загрузку policy. Начни с `solution.py` и `policy.hcl` рядом с этим README. В HCL заполни `path` для единственного KV v2 API-пути `secret/data/housing` и `capabilities` только для чтения. Не добавляй wildcard или root-права. Код функций реализуется в Python, применение policy выполняется отдельными административными CLI-командами.

## Контракты функций

```python
def inspect_payload(payload):
    ...

def read_secret(client, path="housing", mount_point="secret") -> dict:
    ...
```

| Функция и аргумент | Тип и формат | Происхождение и назначение | Пример |
|---|---|---|---|
| `inspect_payload`: `payload` | `dict` ответа KV v2 с вложенными словарями `data.data` | Результат `read_secret_version` или фиксированный вход теста. Проверяется наличие ключа, а не его значение | `{"data": {"data": {"artifact_key": "example-not-a-real-key"}, "metadata": {"version": 1}}}` |
| `read_secret`: `client` | Настроенный `hvac.Client` с интерфейсом `secrets.kv.v2` | CLI создаёт его из адреса, token и timeout. Unit-тест передаёт объект с тем же интерфейсом | `hvac.Client(url=address, token=token, timeout=5)` |
| `read_secret`: `path` | `str`, логическое имя внутри mount, default `"housing"` | Аргумент вызывающего кода или CLI `--path`. Сегмент `data` добавляет SDK | `"housing"`, для отрицательной проверки `"neighbor"` |
| `read_secret`: `mount_point` | `str`, имя KV engine без `/v1/`, default `"secret"` | CLI `--mount` или аргумент теста. Отдельно от имени секрета | `"secret"` |

Обе функции возвращают только `{"field_present": True}`. Пустая строка в `artifact_key` всё ещё означает наличие поля: проверка не оценивает пригодность ключа. Некорректная структура или отсутствие ключа дают `ValueError`. `read_secret` делает один вызов `client.secrets.kv.v2.read_secret_version` с именованными `path` и `mount_point`, затем проверяет payload. Ошибки SDK доходят до вызывающего кода без retry и без печати тела ответа.

## Параметры CLI

| Вход | Формат и происхождение | Пример и смысл |
|---|---|---|
| `VAULT_ADDR`, `--address` | URL сервера. Флаг переопределяет env, затем используется default | `http://127.0.0.1:8200` |
| `VAULT_TOKEN` | Ограниченный application token из текущего shell | Получен административной командой в подготовке. Через CLI-флаг не передаётся |
| `--path` | Логическое имя секрета, default `housing` | `--path housing` |
| `--mount` | Имя KV mount, default `secret` | `--mount secret` |
| `--timeout` | Положительное число секунд, default `5` | `--timeout 3`. Неположительное значение отвергает argparse |

CLI печатает безопасный JSON результата. Forbidden даёт `access_denied`, Timeout — `network_timeout`, другие VaultError — `vault_error` и ненулевой код завершения. Ошибка структуры остаётся `ValueError` функции. Прямой запуск без `VAULT_TOKEN` не создаёт доступ автоматически.

## Выполнение и проверки

Клиент читает один ключ закрытого артефакта. Администратор готовит dev Vault, секрет `secret/housing` и policy. Приложение использует отдельный ограниченный token. Успех с root не проверяет минимальные права.

Заполни обе функции в `solution.py` и task-local policy по контрактам выше. Не возвращай исходный payload, значение ключа, token или текст ошибки SDK. Перед запуском CLI подготовь ограниченный token по [инструкции модуля](../../README.md#подготовка-к-заданиям).

```bash
make task TASK=10-vault/01-policy
MLOPS_RUN_SDK=1 make task TASK=10-vault/01-policy
python scripts/run_task.py run 10-vault/01-policy
```

CLI читает `VAULT_ADDR`/`VAULT_TOKEN`, принимает `--address`, `--path`, `--mount`, `--timeout`. После реализации ожидается только field_present=true. SDK-тест проходит через настоящий hvac KV2 и подменяет лишь transport без сетевого сервиса. Без SDK базовая коллекция работает, SDK-тест пропущен. Незаполненные функции дают NotImplementedError.

На уже подготовленном Vault с ограниченным application token:

```bash
MLOPS_RUN_INTEGRATION=1 make task TASK=10-vault/01-policy
curl -s -o /dev/null -w '%{http_code}\n' -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/housing"
curl -s -o /dev/null -w '%{http_code}\n' -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/neighbor"
```

Live-тест вызывает именно твою `read_secret`: разрешённый путь даёт field_present=true, соседний — Forbidden/403. Он ничего не создаёт и не меняет. `VAULT_DENIED_PATH` позволяет указать другой заведомо запрещённый логический путь. Отрицательная проверка ловит ошибочное использование root. Отдельные curl probes сохранены для диагностики и печатают только коды 200/403. Закончи `unset VAULT_TOKEN`, затем `docker compose -f labs/vault/compose.yaml down`.

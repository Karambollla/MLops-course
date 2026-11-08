# Продлить и отозвать собственный доступ

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

Клиент уже умеет читать `artifact_key`, но его token не действует бесконечно. Полученный 403 и отсутствие ответа по сети требуют разных действий. Здесь ты реализуешь классификацию исхода и две операции над token текущего клиента: продление и отзыв. Смысл TTL и отличие от ротации значения разобраны в [главе](../../README.md#ttl-продление-отзыв-и-ротация).

Редактируй три заготовки в [solution.py](solution.py). CLI уже создаёт `hvac.Client`, выбирает действие и печатает безопасный результат. Секрет и policy остаются после [задания 01](../01-policy/README.md#подготовить-данные-и-ограниченный-token). Для опытов выдаются новые временные token.

## Шаг 1. Различить исходы

```python
def classify_error(status=None, timeout=False):
    ...
```

`status` — полученный HTTP-код (`int`) или `None`, `timeout` — признак, что клиент не получил исход вовремя (`bool`). Функция не выполняет запросов. Верни одну строку:

| Условие | Результат | Что это позволяет решить вызывающему коду |
|---|---|---|
| `timeout=True`, при любом status | `network_timeout` | Ограничить повторы и проверить доступность сети |
| Без timeout, status 403 | `access_denied` | Проверить token, TTL и policy |
| Без timeout, status 200–299 | `ok` | Продолжить обработку полученного результата |
| Все остальные случаи, включая `None` | `http_error` | Разобрать конкретный отказ отдельно |

Например, `(403, True)` даёт `network_timeout`, а 401 без timeout по этому учебному контракту относится к `http_error`. Эта классификация не подтверждает срок token на сервере и не исправляет доступ.

## Шаг 2. Выполнить self-операции SDK

```python
def renew_token(client, increment="60s") -> dict:
    ...

def revoke_token(client) -> dict:
    ...
```

`client` — `hvac.Client`, авторизованный собственным временным token. Для renewal token должен быть renewable. `increment` — запрашиваемая длительность Vault, строка вроде `"45s"`, по умолчанию `"60s"`.

`renew_token` один раз вызывает `client.auth.token.renew_self(increment=increment)`. Из ответа `auth.lease_duration` и `auth.renewable` сформируй `{"ttl_seconds": 60, "renewable": True}` с фактическими значениями сервера. Не вычисляй срок из increment. Поле `auth.client_token`, если оно пришло, в результат не включается и не печатается.

`revoke_token` один раз вызывает `client.auth.token.revoke_self()` без аргументов и после успеха возвращает `{"revoked": True}`. Ошибки обеих SDK-операций передаются вызывающему коду. Истёкший или nonrenewable token нельзя продлить бесконечными повторами.

```bash
make task TASK=10-vault/02-expiry
```

Тесты проверяют границы HTTP-кодов, приоритет timeout, вызов self-методов и отсутствие token в выводе. Они не открывают сеть и не ждут истечения TTL.

## Шаг 3. Наблюдать истечение и отзыв

Для опыта истечения выпусти новый nonrenewable token [командой задания 01](../01-policy/README.md#подготовить-данные-и-ограниченный-token) и передай его в `VAULT_TOKEN`. Сразу проверь чтение, затем повтори после его TTL 60 секунд: 200 сменяется на 403. Код значения в KV при этом не удаляется.

Теперь нужен отдельный token, который разрешает продление. Только на своём dev-стенде:

```bash
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault token create -policy=housing -ttl=60s -renewable=true
read -s VAULT_TOKEN
export VAULT_TOKEN
```

До истечения запусти:

```bash
python modules/10-vault/tasks/02-expiry/solution.py renew --increment 60s
python modules/10-vault/tasks/01-policy/solution.py
python modules/10-vault/tasks/02-expiry/solution.py revoke
python modules/10-vault/tasks/01-policy/solution.py
```

Renewal выводит только TTL и renewable, следующее чтение успешно. Revoke выводит `{"revoked": true}`, последнее чтение завершается `access_denied`. Если token успел истечь, создай новый для повторения опыта.

CLI принимает обязательное действие `renew` или `revoke`, флаг `--increment` (default `60s`) и `--address`. Адрес берётся из `VAULT_ADDR`, при его отсутствии из `http://127.0.0.1:8200`. Флаг выше env по приоритету. Token берётся из `VAULT_TOKEN`, timeout клиента равен 5 секундам. Forbidden, Timeout и прочие VaultError дают соответственно `access_denied`, `network_timeout`, `vault_error` с кодом 1. Чистая `classify_error` сама этим CLI не вызывается.

## Проверка на новом временном token

Автоматическая live-проверка должна сама создать удостоверение, успеть продлить его и отозвать. Для этого ей нужен отдельный административный клиент. В `VAULT_ADMIN_TOKEN` введи token администратора своего dev-стенда без эха. `VAULT_ADDR`, поле `artifact_key` и policy `housing` должны быть подготовлены:

```bash
read -s VAULT_ADMIN_TOKEN
export VAULT_ADMIN_TOKEN
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 make task TASK=10-vault/02-expiry
```

Тест создаёт renewable child с TTL `60s`, вызывает твоё чтение из 01, renewal и revoke, затем проверяет отказ. В `finally` администратор отзывает только созданный тестом child, в том числе при ошибке реализации. Переданные admin/application token не отзываются. `VAULT_TEST_POLICY` позволяет переопределить имя policy, по умолчанию `housing`. Для записи нужны оба флага. Без них тест пропущен.

## Завершение

```bash
unset VAULT_TOKEN VAULT_ADMIN_TOKEN
docker compose -f labs/vault/compose.yaml down
```

Dev-данные исчезнут после удаления контейнера. В проекте остаются код и policy, а значения token и полный вывод их создания не сохраняются.

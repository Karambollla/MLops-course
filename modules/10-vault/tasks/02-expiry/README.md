# TTL, renew и revoke через SDK и CLI

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Аргументы и результаты

```python
def classify_error(status=None, timeout=False):
    ...

def renew_token(client, increment="60s") -> dict:
    ...

def revoke_token(client) -> dict:
    ...
```

| Функция и аргумент | Тип и формат | Откуда берётся и зачем нужен | Пример |
|---|---|---|---|
| `classify_error`: `status` | `int` HTTP-кода либо `None`, default `None` | Уже полученный ответ. Функция не выполняет сеть | `403`, `204`, `None` |
| `classify_error`: `timeout` | `bool`, default `False` | Вызывающий код сообщает, что ожидание ответа завершилось timeout | `True` при `requests.exceptions.Timeout` |
| `renew_token`: `client` | Настроенный `hvac.Client` с `auth.token` | Клиент собственного временного renewable token. В тесте используется double с тем же интерфейсом | Клиент из CLI с `VAULT_ADDR` и `VAULT_TOKEN` |
| `renew_token`: `increment` | `str` длительности Vault, default `"60s"` | Запрашиваемое продление из аргумента функции либо CLI `--increment`. Не обещает фактический TTL | `"45s"` |
| `revoke_token`: `client` | Такой же клиент, авторизованный собственным token | Отзывается именно текущий token через self endpoint | Клиент временного token после renewal |

`classify_error` возвращает строку. Timeout имеет приоритет над status: `(403, True)` даёт `"network_timeout"`. Без timeout код 403 даёт `"access_denied"`, весь диапазон 200–299 — `"ok"`, остальные коды и `None` — `"http_error"`. Например, 401 по этому учебному контракту тоже `http_error`. Функция не проверяет TTL на сервере и не исправляет авторизацию.

`renew_token` вызывает `client.auth.token.renew_self(increment=increment)` один раз. Из ответа `{"auth": {"lease_duration": 60, "renewable": True, ...}}` верни `{"ttl_seconds": 60, "renewable": True}`. Значения берутся из ответа, а не выводятся из increment. Ответ может также содержать `client_token`, его нельзя возвращать или печатать.

`revoke_token` вызывает `client.auth.token.revoke_self()` без чужого token в аргументах и после успеха возвращает `{"revoked": True}`. Forbidden и Timeout обеих SDK-функций передаются вызывающему коду. Nonrenewable или истёкший token нельзя сделать рабочим одной повторной попыткой.

## Запуск и ручной lifecycle

| Вход CLI | Тип и происхождение | Пример |
|---|---|---|
| `action` | Обязательный позиционный аргумент, `renew` или `revoke` | `run 10-vault/02-expiry renew` |
| `--address`, `VAULT_ADDR` | URL сервера. Флаг выше env по приоритету, default `http://127.0.0.1:8200` | `--address http://127.0.0.1:8200` |
| `VAULT_TOKEN` | Собственный временный token в env, прочитанный без эха | Используется внутри `hvac.Client`, не передаётся аргументом token в функцию |
| `--increment` | Строковая длительность, default `60s` | `renew --increment 45s` |

CLI использует timeout 5 секунд. Forbidden печатается как `access_denied`, Timeout — `network_timeout`, другой VaultError — `vault_error`. Эти исходы завершают CLI с кодом 1. `classify_error` остаётся отдельной чистой функцией, CLI не вызывает её автоматически.

Реализуй три функции в `solution.py`. Истечение прав и сетевой timeout требуют разных действий. Подготовка token и SDK описана в [модуле](../../README.md#подготовка-к-заданиям). Базовые тесты не ждут истечения TTL и не открывают сеть:

```bash
make task TASK=10-vault/02-expiry
```

Для ручного опыта создай отдельный краткоживущий nonrenewable token по [подготовке модуля](../../README.md#подготовка-к-заданиям), используй только его в `VAULT_TOKEN` и выполни статусный GET из задания 01 сразу и после TTL60s: 200→403. Дождись срока вручную. Тесты не задерживают прогон на минуту. Отдельно создай renewable token и до истечения проверь:

```bash
python scripts/run_task.py run 10-vault/02-expiry renew --increment 60s
python scripts/run_task.py run 10-vault/02-expiry revoke
```

CLI создаёт настоящий hvac client из `VAULT_ADDR`/`VAULT_TOKEN`. `--address` переопределяет адрес. Renewal печатает только TTL/renewable. После revoke следующий запуск чтения из задания 01 должен закончиться access_denied. Эквивалентные команды Vault CLI: `vault token renew -format=json | jq '{ttl:.auth.lease_duration,renewable:.auth.renewable}'` и `vault token revoke -self`. Используй их только со своим временным token. Revoke не удаляет статическое значение KV.

Живой тест lifecycle **изменяет** состояние и включается отдельно:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 make task TASK=10-vault/02-expiry
```

Нужны установленный SDK, `VAULT_ADDR`, отдельный `VAULT_ADMIN_TOKEN` с правом выдачи/отзыва дочерних token и существующая policy `housing` (либо `VAULT_TEST_POLICY`). Тест сам создаёт временный renewable child TTL60s, проверяет чтение твоей функцией, renewal, revoke и 403 после отзыва. В finally администратор отзывает только созданный в этом тесте child, включая случай NotImplementedError. Переданный admin/application token не отзывается. Marker `writes` позволяет дополнительно выбрать/исключить такие проверки. Без **обоих** opt-in флагов live lifecycle пропущен.

Заверши `unset VAULT_TOKEN VAULT_ADMIN_TOKEN` и останови dev Vault. Токены и полный stdout `token create/lookup` не сохраняй в Git.

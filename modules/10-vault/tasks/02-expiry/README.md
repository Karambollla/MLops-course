# TTL, renew и revoke

## Зачем различать прекращение доступа и сеть

Истёкший token и недоступный сервер не исправляются одним действием. В первом случае клиент уже получил ответ об отказе, во втором не получил результат вовремя. Неправильный бесконечный retry с 403 скрывает причину и создаёт лишние запросы.

Исходное состояние — dev Vault с секретом и policy из задания 01. HTTP-коды для функции заданы явно, поэтому её тесты не требуют сервера. Реальные TTL/renew/revoke изучаются отдельным ручным опытом. Прочти [жизненный цикл token](../../README.md#ttl-продление-отзыв-и-ротация) и [ответственность клиента](../../README.md#интеграция-с-pod-и-ответственность-приложения).

## Контракт классификации

`classify_error(status=None, timeout=False)` возвращает один из четырёх строковых исходов. Timeout имеет приоритет: например, `(status=None, timeout=True)` даёт `network_timeout`; `(403, False)` — `access_denied`. В HTTP-ветке 200 и 204 — `ok`, 404/500 — `http_error`. Функция не продлевает token и не обращается к Vault. Во время живого опыта истечение или revoke меняет результат разрешённого чтения 200→403, но не удаляет статический ключ из KV.

## Реализация и опыт

Реализуй `classify_error(status=None, timeout=False)`: timeout→network_timeout, 403→access_denied, 2xx→ok, прочие HTTP-коды→http_error. Не добавляй бесконечный retry при 403.

```bash
make task TASK=10-vault/02-expiry
```

В dev Vault вручную создай ограниченный nonrenewable token с TTL60s по практике модуля. Выполни только статусный GET из задания 01 сразу и после TTL: ожидается 200→403. Не печатай response body. Отдельно с renewable token выполни `vault token renew` до истечения и наблюдай увеличенный TTL, затем `vault token revoke -self`: следующий GET должен вернуть 403. Renew/revoke меняют состояние и выполняются только тобой, не тестами. Для безопасного отображения renewal используй `vault token renew -format=json | jq '{ttl:.auth.lease_duration,renewable:.auth.renewable}'`. Не записывай stdout полного token create/lookup в Git.

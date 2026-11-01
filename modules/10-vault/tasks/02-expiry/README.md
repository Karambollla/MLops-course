# TTL, renew и revoke

Реализуй `classify_error(status=None, timeout=False)`: timeout→network_timeout, 403→access_denied, 2xx→ok, прочие HTTP-коды→http_error. Не добавляй бесконечный retry при 403.

```bash
make task TASK=10-vault/02-expiry
```

В dev Vault вручную создай ограниченный nonrenewable token с TTL60s по практике модуля. Выполни только статусный GET из задания 01 сразу и после TTL: ожидается 200→403. Не печатай response body. Отдельно с renewable token выполни `vault token renew` до истечения и наблюдай увеличенный TTL, затем `vault token revoke -self`: следующий GET должен вернуть 403. Renew/revoke меняют состояние и выполняются только тобой, не тестами. Для безопасного отображения renewal используй `vault token renew -format=json | jq '{ttl:.auth.lease_duration,renewable:.auth.renewable}'`. Не записывай stdout полного token create/lookup в Git. Никакой JSON наблюдений заполнять не нужно.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

# TTL, renew и revoke через SDK и CLI

[Теория](../../README.md) · [Подготовка Vault](../../practice.md)

Истечение token, отказ policy и timeout требуют разных действий. `classify_error(status=None,timeout=False)` сохраняется чистой функцией: timeout→network_timeout (приоритет), 403→access_denied, 2xx→ok, остальное→http_error. Запрос или бесконечный retry она не выполняет.

Реализуй также `renew_token(client,increment="60s")` и `revoke_token(client)`. Первая использует `client.auth.token.renew_self` и возвращает **только** `{"ttl_seconds":60,"renewable":true}` из метаданных ответа. Вторая использует `client.auth.token.revoke_self` и возвращает `{"revoked":true}` после успешного отзыва. Значение token, полный auth-ответ и секреты не попадают в return/logs. Не принимай чужой token аргументом. Forbidden/Timeout передаются вызывающему коду; renewal не делает nonrenewable token продлеваемым.

```bash
make task TASK=10-vault/02-expiry
```

Для ручного опыта создай отдельный краткоживущий nonrenewable token по практике, используй только его в `VAULT_TOKEN` и выполни статусный GET из задания 01 сразу и после TTL60s: 200→403. Дождись срока вручную; тесты не задерживают прогон на минуту. Отдельно создай renewable token и до истечения проверь:

```bash
python scripts/run_task.py run 10-vault/02-expiry renew --increment 60s
python scripts/run_task.py run 10-vault/02-expiry revoke
```

CLI создаёт настоящий hvac client из `VAULT_ADDR`/`VAULT_TOKEN`; `--address` переопределяет адрес. Renewal печатает только TTL/renewable. После revoke следующий запуск чтения из задания 01 должен закончиться access_denied. Эквивалентные команды Vault CLI: `vault token renew -format=json | jq '{ttl:.auth.lease_duration,renewable:.auth.renewable}'` и `vault token revoke -self`. Используй их только со своим временным token. Revoke не удаляет статическое значение KV.

Живой тест lifecycle **изменяет** состояние и включается отдельно:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 make task TASK=10-vault/02-expiry
```

Нужны установленный SDK, `VAULT_ADDR`, отдельный `VAULT_ADMIN_TOKEN` с правом выдачи/отзыва дочерних token и существующая policy `housing` (либо `VAULT_TEST_POLICY`). Тест сам создаёт временный renewable child TTL60s, проверяет чтение твоей функцией, renewal, revoke и 403 после отзыва. В finally администратор отзывает только созданный в этом тесте child, включая случай NotImplementedError. Переданный admin/application token не отзывается. Marker `writes` позволяет дополнительно выбрать/исключить такие проверки. Без **обоих** opt-in флагов live lifecycle пропущен.

Заверши `unset VAULT_TOKEN VAULT_ADMIN_TOKEN` и останови dev Vault. Токены и полный stdout `token create/lookup` не сохраняй в Git.

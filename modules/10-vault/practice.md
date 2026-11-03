# Практика: Vault: секреты и жизненный цикл доступа

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Минимальные права](tasks/01-policy/README.md) | [Старт](tasks/01-policy/solution.py) · [Тесты функций](tasks/01-policy/test_task.py) | cpu |
| [Истечение](tasks/02-expiry/README.md) | [Старт](tasks/02-expiry/solution.py) · [Тесты функций](tasks/02-expiry/test_task.py) | cpu |
| [Интеграционное решение](tasks/03-integration/README.md) | Руководство с примерами | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=10-vault/01-policy
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Функции проверяются прямо на фиксированных входах. Read-only live-проверки читают существующий стенд только с `MLOPS_RUN_INTEGRATION=1`. Lifecycle tests дополнительно требуют `MLOPS_RUN_WRITES=1` и работают только с самостоятельно созданными временными token; guides не требуют отдельной сдачи.

## SDK

После основного SETUP установи необязательную зависимость:

```bash
python -m pip install -r labs/vault/requirements.txt
MLOPS_RUN_SDK=1 make task TASK=10-vault/01-policy
```

Импорт не открывает соединений. SDK-тест использует настоящий hvac KV2 и transport double; доступ/права проверяются отдельно на живом dev Vault. Незавершённые `read_secret`, `inspect_payload`, `renew_token`, `revoke_token`, `classify_error` остаются student-заготовками.

## Подготовка

```bash
docker compose -f labs/vault/compose.yaml up -d
```

Лимит контейнера — 1 ГиБ с учётом пускового расхода памяти на ARM64. Низкое потребление после старта не доказывает достаточность лимита для запуска.

Команды настройки выполняй внутри контейнера с root только на этом стенде:

```bash
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault kv put secret/housing artifact_key=local-demo-value
```

Скопируй policy в контейнер и создай ограниченный token:

```bash
docker compose -f labs/vault/compose.yaml cp modules/10-vault/tasks/01-policy/policy.hcl vault:/tmp/policy.hcl
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault policy write housing /tmp/policy.hcl
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault token create -policy=housing -ttl=60s -renewable=false
```

Для SDK-чтения задай `VAULT_ADDR=http://127.0.0.1:8200` и ограниченный token в `VAULT_TOKEN` в текущем shell. Не вставляй token в командную строку/файл; например, `read -s VAULT_TOKEN` и затем `export VAULT_TOKEN`.

```bash
export VAULT_ADDR=http://127.0.0.1:8200
python scripts/run_task.py run 10-vault/01-policy
MLOPS_RUN_INTEGRATION=1 make task TASK=10-vault/01-policy
```

Поле artifact_key остаётся внутри клиента, stdout содержит только факт наличия; соседний path запрещён. Для ручного renewal создай **новый** token командой подготовки с `-renewable=true`, используй его в `VAULT_TOKEN` и выполни CLI задания 02. Для автоматического lifecycle live-теста администратор передаётся отдельно через `VAULT_ADMIN_TOKEN`, application token не используется для создания дочерних:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 make task TASK=10-vault/02-expiry
```

Тест создаёт свой child TTL60s, вызывает student SDK renew/revoke, проверяет 403 и очищает child в finally. Он не создаёт policy/секреты и не отзывает переданный admin token. Без обоих opt-in флагов writes пропущены.

## Завершение

`unset VAULT_TOKEN VAULT_ADMIN_TOKEN`, затем `docker compose -f labs/vault/compose.yaml down`. Dev-секреты исчезнут. Не сохраняй root/token в файлы проекта.

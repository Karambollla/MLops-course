# Практика: Vault: секреты и жизненный цикл доступа

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Минимальные права](tasks/01-policy/README.md) | [Заготовка](tasks/01-policy/solution.py) · [тесты](tasks/01-policy/test_task.py) | cpu |
| [Истечение](tasks/02-expiry/README.md) | [Заготовка](tasks/02-expiry/solution.py) · [тесты](tasks/02-expiry/test_task.py) | cpu |
| [Интеграционное решение](tasks/03-integration/README.md) | [Заготовка](tasks/03-integration/report.json) · [тесты](tasks/03-integration/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=10-vault/01-policy
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

```bash
docker compose -f labs/vault/compose.yaml up -d
```

Лимит контейнера установлен в 1 ГиБ: при проверке на ARM64 прежние 256 МиБ приводили к OOMKilled во время старта. Низкое потребление после старта не доказывает достаточность лимита для запуска.

Команды настройки выполняй внутри контейнера с root только на этом стенде:

```bash
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault kv put secret/housing artifact_key=local-demo-value
```

Скопируй policy в контейнер и создай ограниченный token:

```bash
docker compose -f labs/vault/compose.yaml cp labs/vault/policy.hcl vault:/tmp/policy.hcl
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault policy write housing /tmp/policy.hcl
docker compose -f labs/vault/compose.yaml exec -e VAULT_TOKEN=course-root vault vault token create -policy=housing -ttl=60s -renewable=false
```

## Завершение

`unset VAULT_TOKEN`, затем `docker compose -f labs/vault/compose.yaml down`. Dev-секреты исчезнут. Не сохраняй root/token в отчёт или shell-скрипт проекта.

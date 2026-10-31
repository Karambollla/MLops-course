# Практика: Vault: секреты и жизненный цикл доступа

[Теория](README.md) · [Подсказки](hints.md)

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

## Задание 1. Минимальные права

Передай выданный token в `VAULT_TOKEN` своего терминала, `VAULT_ADDR=http://127.0.0.1:8200`. Доработай `labs/vault/read_secret.py`: подтвердить наличие нужного ключа без печати значения. Чтение housing успешно; чтение другого пути и запись с этим token запрещены. Сохрани только HTTP-коды и маскированный отчёт.

## Задание 2. Истечение

Через 60 секунд повтори запрос: ожидается 403. Обработай отказ отдельно от сетевого timeout; исключи бесконечный retry. Дополнительно выдай renewable token и исследуй renew/revoke, сохраняя ограниченную policy.

## Задание 3. Интеграционное решение

Опиши, где именно housing-сервису действительно нужен секрет: скачивание приватного артефакта или внешняя зависимость. Для локального read-only файла токен не нужен. Спроектируй Kubernetes auth без внедрения root token в Pod.

## Критерии готовности

- [ ] Позитивный и два отрицательных сценария проверены.
- [ ] Истечение доступа обнаруживается и не превращается в бесконечный retry.
- [ ] Объяснены secret zero, TTL, policy и отличие KV от dynamic secrets.

## Завершение

`unset VAULT_TOKEN`, затем `docker compose -f labs/vault/compose.yaml down`. Dev-секреты исчезнут. Не сохраняй root/token в отчёт или shell-скрипт проекта.

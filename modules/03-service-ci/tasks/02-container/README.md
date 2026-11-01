# Образ и работающий контейнер

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [SETUP](../../../../SETUP.md)

## Зачем проверять собранную поставку

TestClient из [предыдущей темы](../01-api-contract/README.md) работает в Python-процессе теста. Он не проверяет, что образ содержит нужные зависимости, сервер слушает доступный адрес и модель читается из mount под непривилегированным пользователем. Здесь входом становится настоящая поставка: image + собственный bundle + Compose-конфигурация. Роли разобраны в [разделе про образ и адрес](../../README.md#как-образ-получает-модель-и-адрес).

## Исходное состояние и контракт проверки

Нужны Docker daemon с Compose, готовый Dockerfile/API и экспорт кандидата в `work/artifacts/`. Ты управляешь запуском и остановкой стенда; тесты только читают его состояние и вызывают HTTP. `MLOPS_CONTAINER_ID` указывает конкретный запущенный контейнер, `MLOPS_RUN_INTEGRATION=1` разрешает проверки. Пропуск без флага не подтверждает, что образ работает.

Например, при существующем собственном `model.joblib` `/ready` даёт 200 и версию bundle, а inspect показывает `/models` с `RW=false`. В отдельном опыте с пустым mount процесс остаётся жив, `/ready` даёт 503. Если контейнер упал с import error, это не успешный опыт отсутствующей модели: сначала исправь сборку. Порт 8000 на host должен быть свободен, а путь host `work/artifacts` внутри контейнера называется `/models`.

## Что выполнить

Используй `labs/housing/Dockerfile`, `.dockerignore` и Compose. Подготовь собственную модель и перенеси её готовым export.py задания кандидата в `work/artifacts/`. Решение API уже предоставлено; здесь проверяется его работа в контейнере, а не JSON с описанием результата.

Останови локальный Uvicorn, если он занимает порт 8000. Из корня:

```bash
docker compose -f labs/housing/compose.yaml config --quiet
docker compose -f labs/housing/compose.yaml up -d --build
MLOPS_CONTAINER_ID=$(docker compose -f labs/housing/compose.yaml ps -q api) \
  MLOPS_RUN_INTEGRATION=1 make task TASK=03-service-ci/02-container
```

Тесты читают настоящий docker inspect/image inspect, проверяют UID через `id -u`, read-only mount и HTTP-ответы. Они не запускают, не меняют и не удаляют контейнеры. Если API доступен по другому адресу, задай `MLOPS_HOUSING_URL`. Без флага интеграционные тесты пропускаются: это не подтверждение выполнения задания.

## Ожидаемое поведение

```text
GET /live              → 200
GET /ready             → 200
POST /predict          → 200, один конечный прогноз для request.json
POST /predict, []      → 422
id -u                  → ненулевой UID
mount /models          → RW=false
```

Число и версия модели берутся из твоего bundle; фиксированный пример прогноза не требуется. Состав контекста проверь по Dockerfile и .dockerignore: CSV, секреты и локальная venv не должны копироваться в образ приложения.

## Проверка отсутствующей модели

Используй отдельный стенд с пустой папкой моделей. Не удаляй собственную модель. Можно создать временную Compose-надстройку в work:

```bash
mkdir -p work/empty-models
cat > work/housing-empty.compose.yaml <<'YAML'
services:
  api:
    volumes:
      - ../../work/empty-models:/models:ro
YAML
```

Путь в надстройке задан относительно первого Compose-файла, labs/housing/compose.yaml. Останови основной стенд и запусти отдельный проект:

```bash
docker compose -f labs/housing/compose.yaml down
docker compose -p housing-empty -f labs/housing/compose.yaml -f work/housing-empty.compose.yaml up -d
MLOPS_CONTAINER_ID=$(docker compose -p housing-empty -f labs/housing/compose.yaml -f work/housing-empty.compose.yaml ps -q api) \
  MLOPS_MODEL_STATE=absent MLOPS_RUN_INTEGRATION=1 make task TASK=03-service-ci/02-container
```

Теперь ожидаются `/live` → 200, `/ready` и валидный `/predict` → 503; неверный запрос по-прежнему даёт 422. Ошибка импорта или падение контейнера не является ожидаемым результатом отсутствующей модели.

## Остановка

```bash
docker compose -p housing-empty -f labs/housing/compose.yaml -f work/housing-empty.compose.yaml down
docker compose -f labs/housing/compose.yaml down
```

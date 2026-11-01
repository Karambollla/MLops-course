# Образ

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Основной starter: `modules/03-service-ci/tasks/02-container/evidence.json`. Заполни его реальными Docker/HTTP результатами. Используй общие `labs/housing/Dockerfile`, `.dockerignore` и `compose.yaml`; инфраструктуру курса не копируй. При необходимости автоматизируй сбор в физическом `solution.py`: `collect_evidence(container_id: str, base_url: str, request_path: Path) -> dict`; функция делает только read-only inspect/HTTP и возвращает схему evidence.json. Сборщик необязателен, свидетельства можно заполнить вручную.

Схема: user — эффективный пользователь образа; model_read_only — mount модели readonly; embedded_paths — найденные в образе CSV/веса/секреты/venv (ожидается []); ready_status; predictions_count для request.json; image_id с sha256:; dependency_versions с python; image_size_bytes. Добавь without_model_ready_status=503, without_model_predict_status=503, without_model_live_status=200 и model_removed_only_in_temporary_copy=true по отдельному опыту. Не выдумывай значения: приложи команды и вывод в report.md. Проверка JSON не доказывает фактический состав image, это проверяется вручную по Dockerfile/context/inspect.

## Среда и зависимости

Базовая среда из SETUP: Python, pytest; CPU, Linux/macOS.

Зависит от 03-service-ci/01-api-contract. Нужен Docker Desktop/Compose для ручной проверки. Останови Uvicorn (порт 8000), выполни compose config/up из практики, curl ready/predict; сохрани image ID, размер и зависимости. Шаблон evidence.json — ввод для audit_container; fixture не является результатом реального Docker.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=03-service-ci/02-container
```

До заполнения evidence.json ожидается RED на незаполненных значениях; сборщик solution.py отдельно содержит NotImplementedError. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

CLI solution.py не требуется. Для opt-in проверки уже поднятого API: `MLOPS_RUN_INTEGRATION=1 make task TASK=03-service-ci/02-container`. Она выполняет только GET readiness.

## Требования практического опыта

Останови локальный Uvicorn предыдущего задания через Ctrl+C: Compose использует тот же host port 8000.

```bash
docker compose -f labs/housing/compose.yaml config --quiet
docker compose -f labs/housing/compose.yaml up -d --build
curl -i http://localhost:8000/ready
curl -sS http://localhost:8000/predict -H 'Content-Type: application/json' --data-binary @labs/housing/request.json
```

При готовой модели ожидаются 200 и один prediction. Сохрани image ID, версии зависимостей и размер образа. Удали модель только в отдельной временной копии и проверь ожидаемый 503 после перезапуска.

## Приёмка и очистка

Пройди все тесты `test_task.py`, сохрани перечисленные артефакты и добавь объяснение решений/ограничений в `report.md`. Для инфраструктурных опытов приложи реальные команды и вывод: offline проверки не доказывают развёртывание, доступность удалённого сервера или качество объяснения. Ручная оценка: воспроизводимость шагов, соответствие исходному контракту, объяснение причины сбоя и корректное восстановление.

После опыта останови стенд: `docker compose -f labs/housing/compose.yaml down`. Uvicorn останови Ctrl+C. Не удаляй volume без экспорта истории; артефакты `work/` сохрани для следующих модулей.

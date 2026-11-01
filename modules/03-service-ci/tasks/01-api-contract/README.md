# Контракт

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Редактируй `modules/03-service-ci/tasks/01-api-contract/solution.py` (физическая заготовка рядом). Дополнительные свои тесты и `report.md` размещай в этой же папке. Полных решений в заготовке нет.

`check_prediction_response(payload: dict, expected, model_version: str) -> None` проверяет ровно ключи predictions/model_version/target_unit, размер batch, конечные прогнозы и allclose с rtol=1e-6, atol=1e-8; единица "100000 USD"; нарушение — ValueError. `exercise_api(client, pipeline, batch, model_version: str) -> None`: client — FastAPI TestClient уже в lifespan, batch — DataFrame FEATURES; сравни HTTP /predict и Pipeline, переставь JSON-ключи, проверь пустой/257 batch, missing/extra поля, строки/bool вместо чисел и NaN/Infinity → 422. При отсутствии модели проверь live=200, ready/predict=503 отдельным тестом. Физически добавь свои интеграционные тесты в эту папку, используя shared housing.api; код API уже предоставлен, не создавай второй сервер. Несовместимый bundle должен сорвать startup.

## Среда и зависимости

Базовая среда, fastapi/httpx/joblib/pandas/numpy/sklearn из housing; CPU.

Зависит от 01-ml/02-candidate и манифеста. Сверь имя payload с labs/housing/request.json и API. Тесты создают только свой доверенный bundle, сеть не нужна.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=03-service-ci/01-api-contract
```

До реализации ожидается RED: `NotImplementedError`, а не ошибка импорта зависимостей. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

Это задание использует функции; импортируй заготовку через `course_tasks.load_task("03-service-ci/01-api-contract")` из Python. CLI не требуется.

## Требования практического опыта

```bash
make test
uvicorn housing.api:app --host 127.0.0.1 --port 8000
```

Без модели проверь `/live` → 200, `/ready` → 503, валидный `/predict` → 503. С обученным bundle `/ready` и `/predict` возвращают 200. Запрос есть в `labs/housing/request.json`.

Добавь интеграционные тесты: совпадение predict HTTP и pipeline, перестановка JSON-ключей, NaN/Infinity, несовместимый bundle и неправильное количество строк. Неверная схема запроса должна давать 422 до выполнения модели.

## Приёмка и очистка

Пройди все тесты `test_task.py`, сохрани перечисленные артефакты и добавь объяснение решений/ограничений в `report.md`. Для инфраструктурных опытов приложи реальные команды и вывод: offline проверки не доказывают развёртывание, доступность удалённого сервера или качество объяснения. Ручная оценка: воспроизводимость шагов, соответствие исходному контракту, объяснение причины сбоя и корректное восстановление.

После опыта останови стенд: `docker compose -f labs/housing/compose.yaml down`. Uvicorn останови Ctrl+C. Не удаляй volume без экспорта истории; артефакты `work/` сохрани для следующих модулей.

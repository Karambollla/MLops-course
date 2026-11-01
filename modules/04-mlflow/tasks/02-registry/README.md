# Registry

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Редактируй `modules/04-mlflow/tasks/02-registry/solution.py` (физическая заготовка рядом). Дополнительные тесты размещай в этой же папке. Полных решений в заготовке нет.

`resolve_release(client, model_name: str, alias: str, expected_run_id: str) -> dict`: client предоставляет get_model_version_by_alias(name, alias); возвращает {model_name, alias, version: str, run_id, model_uri: "models:/NAME/VERSION"}; номер версии — положительное целое, run_id совпадает, иначе ValueError. Никогда не сохраняй models:/NAME@champion как финальную ссылку. `register_model(pipeline, example, run_id: str, model_name: str, tracking_uri: str) -> dict`: mlflow.sklearn.log_model именно Pipeline с input_example/signature в исходном run, зарегистрируй, назначь candidate и champion только после quality gate и финального test, верни разрешённый release. `assert_parity(original, registered, batch) -> None`: allclose rtol=1e-6, atol=1e-8 с одинаковыми размерами и конечностью, иначе ValueError. Сохрани release.json и проверь исходный bundle против загруженной registry-модели.

## Среда и зависимости

Базовая среда, numpy; реальные Registry действия требуют MLflow SDK/Compose предыдущего задания; CPU.

Зависит от 04-mlflow/01-experiments. Офлайн fake client проверяет разрешение версии, а не MLflow сервер. Ожидаемое поведение на стенде: input example/signature доступны, release ссылается на исходный run, прогнозы совпадают, после рестарта метаданные/artifacts остаются.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=04-mlflow/02-registry
```

До реализации ожидается RED: `NotImplementedError`, а не ошибка импорта зависимостей. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

Это задание использует функции; импортируй заготовку через `course_tasks.load_task("04-mlflow/02-registry")` из Python. CLI не требуется.

## Требования практического опыта

Через `mlflow.sklearn.log_model` зарегистрируй Pipeline с input example и signature. Через MlflowClient назначь `candidate` и `champion`. Разреши champion в конкретный номер версии и сохрани release manifest. Выполни predict через исходный bundle и загруженную зарегистрированную модель на одинаковом batch; результаты должны совпасть в допуске.

## Приёмка и очистка

Выполни `test_task.py`: проверяются результаты функций, ошибки входа и изменения технических артефактов. Письменный пересказ выполнения не требуется.

После опыта останови стенд: `docker compose -f labs/mlflow/compose.yaml down`. Uvicorn останови Ctrl+C. Не удаляй volume без экспорта истории; артефакты `work/` сохрани для следующих модулей.

## Пример корректного результата

Разрешённый release хранит конкретную строковую версию и URI вида models:/housing/7, а не плавающий alias. Несовпадение expected_run_id вызывает ValueError. Прогноз зарегистрированной модели совпадает с исходным Pipeline в заданном допуске.

# Registry

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Зачем после run нужна версия выпуска

Run из [предыдущей темы](../01-experiments/README.md) описывает обучение. Сервису требуется точный загружаемый объект с понятным интерфейсом, который не изменится при следующем выборе champion. Registry даёт имя семейства и конкретные версии, а release закрепляет выбранную версию. Различия bundle, MLflow Model, flavor, signature и alias разобраны в [теории регистрации](../../README.md#от-pipeline-к-версии-реестра).

## Исходный результат и новые действия

Нужны выбранный по validation run ID, его обученный Pipeline, небольшой batch-пример с FEATURES и результаты финальной проверки качества. Сервер предыдущей темы остаётся тем же: нельзя зарегистрировать модель в другой истории и ожидать прежнюю связь run. В заготовке реализуются регистрация, разрешение alias и проверка численного паритета; итог сохраняется как `release.json`.

Импорты `mlflow` и `mlflow.sklearn` уже находятся в начале файла. В `register_model` предстоит применить `mlflow.models.infer_signature` и `mlflow.sklearn.log_model`, а через `MlflowClient` — получить версию и назначить alias. Это учебная реализация: до её завершения SDK не регистрирует модель автоматически. Различие файла артефакта и формата MLflow Model объясняется в [разделе о версии реестра](../../README.md#от-pipeline-к-версии-реестра).

Если `champion` указывает на версию 7 исходного `run-1`, `resolve_release(..., expected_run_id="run-1")` возвращает URI `models:/housing/7` и version `"7"`. Если alias теперь ведёт к другому run, нужен `ValueError`, даже при подходящем имени модели. После загрузки модели по закреплённому URI один batch должен дать те же конечные прогнозы, что исходный Pipeline. Проверка версии и проверка чисел независимы: неверный источник иногда может случайно вернуть те же числа на маленьком примере.

## Где работать и контракт

Редактируй `modules/04-mlflow/tasks/02-registry/solution.py`. Дополнительные тесты размещай в этой же папке.

`resolve_release(client, model_name: str, alias: str, expected_run_id: str) -> dict`: client предоставляет get_model_version_by_alias(name, alias); возвращает {model_name, alias, version: str, run_id, model_uri: "models:/NAME/VERSION"}; номер версии — положительное целое, run_id совпадает, иначе ValueError. Никогда не сохраняй models:/NAME@champion как финальную ссылку. `register_model(pipeline, example, run_id: str, model_name: str, tracking_uri: str) -> dict`: mlflow.sklearn.log_model именно Pipeline с input_example/signature в исходном run, зарегистрируй, назначь candidate и champion только после quality gate и финального test, верни разрешённый release. `assert_parity(original, registered, batch) -> None`: allclose rtol=1e-6, atol=1e-8 с одинаковыми размерами и конечностью, иначе ValueError. Сохрани release.json и проверь исходный bundle против загруженной registry-модели.

## Среда и зависимости

Базовая среда, numpy; реальные Registry действия требуют MLflow SDK/Compose предыдущего задания; CPU.

Зависит от 04-mlflow/01-experiments. Офлайн fake client проверяет разрешение версии, а не MLflow сервер. Ожидаемое поведение на стенде: input example/signature доступны, release ссылается на исходный run, прогнозы совпадают, после рестарта метаданные/artifacts остаются.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=04-mlflow/02-registry
```

Тесты функций работают offline на маленьких входах и временных файлах. До реализации ожидается `NotImplementedError`; ошибка импорта означает проблему подготовки среды. Проверка функций не заменяет описанный опыт на данных или стенде.

Это задание использует функции; импортируй заготовку через `course_tasks.load_task("04-mlflow/02-registry")` из Python. CLI не требуется.

## Требования практического опыта

Через `mlflow.sklearn.log_model` зарегистрируй Pipeline с input example и signature. Через MlflowClient назначь `candidate` и `champion`. Разреши champion в конкретный номер версии и сохрани release manifest. Выполни predict через исходный bundle и загруженную зарегистрированную модель на одинаковом batch; результаты должны совпасть в допуске.

## Приёмка и очистка

Запусти указанную выше команду `make task` после реализации и исправления ошибок. Проверяемые случаи перечислены в соседнем `test_task.py`.

После опыта останови стенд: `docker compose -f labs/mlflow/compose.yaml down`. Не удаляй volume без экспорта истории; артефакты `work/` сохрани для следующих модулей.

## Пример корректного результата

Разрешённый release хранит конкретную строковую версию и URI вида models:/housing/7, а не плавающий alias. Несовпадение expected_run_id вызывает ValueError. Прогноз зарегистрированной модели совпадает с исходным Pipeline в заданном допуске.

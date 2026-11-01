# Три запуска

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Редактируй `modules/04-mlflow/tasks/01-experiments/solution.py` (физическая заготовка рядом). Дополнительные свои тесты и `report.md` размещай в этой же папке. Полных решений в заготовке нет.

`select_candidate(runs: list[dict]) -> str`: ровно три FINISHED run с разными parameters, одинаковыми data_sha256/split, конечными неотрицательными validation_mae/validation_rmse; выбери минимум (validation_mae, run_id), верни run_id; при нарушении ValueError. Test-метрики не влияют на выбор. `track_experiments(data: Path, output: Path, tracking_uri: str) -> list[dict]` реально обучает три конфигурации на одном split и пишет MLflow experiment housing-course: параметры, data_sha256, split, версии, MAE/RMSE, model bundle. Возвращает записи для select_candidate, сохраняет comparison.json. MLflow импортируй внутри функции, не во время collection. Логируй измеренные метрики; не дублируй train, используй собственный candidate и расширь его конфигурацию при необходимости.

## Среда и зависимости

Базовая среда; MLflow SDK из labs/mlflow/requirements.txt в отдельном окружении, housing установлен --no-deps -e; CPU.

Зависит от train и 02-reproducibility. Для реальных запусков подними labs/mlflow/compose.yaml, URI <http://127.0.0.1:5001>, используй track_experiments из Python. Сохрани IDs и объяснение выбора в report.md; офлайн-тест не доказывает, что run реально загружен на сервер.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=04-mlflow/01-experiments
```

До реализации ожидается RED: `NotImplementedError`, а не ошибка импорта зависимостей. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

Это задание использует функции; импортируй заготовку через `course_tasks.load_task("04-mlflow/01-experiments")` из Python. CLI не требуется.

## Требования практического опыта

Реализуй `track_experiments` в `solution.py`: три разных конфигурации на одном split, параметры, MAE/RMSE, data_sha256, split и model bundle. Сделай таблицу сравнения validation. Не подбирай по test.

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 python modules/04-mlflow/tasks/01-experiments/solution.py
```

Ожидаются три завершённых run в experiment `housing-course`. Сохрани run IDs и объяснение выбора.

## Приёмка и очистка

Пройди все тесты `test_task.py`, сохрани перечисленные артефакты и добавь объяснение решений/ограничений в `report.md`. Для инфраструктурных опытов приложи реальные команды и вывод: offline проверки не доказывают развёртывание, доступность удалённого сервера или качество объяснения. Ручная оценка: воспроизводимость шагов, соответствие исходному контракту, объяснение причины сбоя и корректное восстановление.

После опыта останови стенд: `docker compose -f labs/mlflow/compose.yaml down`. Uvicorn останови Ctrl+C. Не удаляй volume без экспорта истории; артефакты `work/` сохрани для следующих модулей.

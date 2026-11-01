# Три запуска

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Зачем объединять три обучения

У тебя уже есть `train`, который создаёт bundle и метрики. Теперь нужно сравнить настройки, сохранив связь каждого числа с его моделью и входами. MLflow хранит эти записи, а твой код определяет, какие запуски сопоставимы и кто победил по validation. Сначала прочти [путь метаданных и файлов](../../README.md#путь-параметров-метрик-и-файлов) и [правила сравнения](../../README.md#сравнимые-запуски-и-выбор).

## Что нужно подготовить

Нужны собственный [train кандидата](../../../01-ml/tasks/02-candidate/README.md), [манифест](../../../02-reproducibility/tasks/02-manifest/README.md), один `work/housing.csv` и один split. В отдельной среде MLflow SDK должен обращаться к поднятому Compose по `http://127.0.0.1:5001`. Заготовка содержит CLI, импорт `mlflow` в начале файла и проверку наличия SDK. Реализуются `track_experiments` и чистая проверка/выбор `select_candidate`; само наличие импорта ещё не записывает запуск.

Внутри `track_experiments` понадобятся `set_tracking_uri`, `set_experiment`, контекст `start_run`, а затем `log_params`, `log_metrics` и `log_artifacts` с результатами собственного обучения. Их назначение и маленький рабочий пример разобраны в [самостоятельном примере SDK](../../README.md#самостоятельный-пример-учёта). Отсутствие необязательного пакета обрабатывается по [общему стандарту импортов](../../../../docs/task-structure.md#импорты).

Представь три FINISHED run A/B/C с одинаковыми SHA/split, разными `parameters` и validation MAE 0.8/0.5/0.6. Результат выбора — ID B, даже если test A лучше. При смене SHA у B должен возникнуть отказ вместо «победителя»: сравнение стало несопоставимым. Реальный выход `track_experiments` — три записи на сервере, их файлы и `comparison.json`; маленький offline-тест выбора подтверждает только правило отбора, а не факт обучения и загрузки artifacts.

## Где работать и контракт

Редактируй `modules/04-mlflow/tasks/01-experiments/solution.py`. Дополнительные тесты размещай в этой же папке.

`select_candidate(runs: list[dict]) -> str`: ровно три FINISHED run с разными parameters, одинаковыми data_sha256/split, конечными неотрицательными validation_mae/validation_rmse; выбери минимум (validation_mae, run_id), верни run_id; при нарушении ValueError. Test-метрики не влияют на выбор. `track_experiments(data: Path, output: Path, tracking_uri: str) -> list[dict]` реально обучает три конфигурации на одном split и пишет MLflow experiment housing-course: параметры, data_sha256, split, версии, MAE/RMSE, model bundle. Возвращает записи для select_candidate, сохраняет comparison.json. Логируй измеренные метрики; не дублируй train, используй собственный candidate и расширь его конфигурацию при необходимости.

## Среда и зависимости

Базовая среда; MLflow SDK из labs/mlflow/requirements.txt в отдельном окружении, housing установлен --no-deps -e; CPU.

Зависит от train и 02-reproducibility. Для реальных запусков подними labs/mlflow/compose.yaml, URI <http://127.0.0.1:5001>, используй track_experiments из Python. Проверь runs в UI/API MLflow; офлайн-тест выбора кандидата не проверяет запись на сервер.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=04-mlflow/01-experiments
```

Тесты функций работают offline на маленьких входах и временных файлах. До реализации ожидается `NotImplementedError`; ошибка импорта означает проблему подготовки среды. Проверка функций не заменяет описанный опыт на данных или стенде.

Функции доступны через `course_tasks.load_task("04-mlflow/01-experiments")`; CLI `solution.py` также предоставлен. Он принимает `--data` (по умолчанию `work/housing.csv`), `--output` (`work/mlflow-runs`) и `--tracking-uri` (сначала переменная `MLFLOW_TRACKING_URI`, иначе `http://127.0.0.1:5001`). Явный аргумент выбирает конкретный сервер для данного запуска.

## Требования практического опыта

Реализуй `track_experiments` в `solution.py`: три разных конфигурации на одном split, параметры, MAE/RMSE, data_sha256, split и model bundle. Сделай таблицу сравнения validation. Не подбирай по test.

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 python modules/04-mlflow/tasks/01-experiments/solution.py
```

Ожидаются три завершённых run в experiment `housing-course`. Проверь реальные run IDs в UI/API и выбор кандидата по validation MAE.

## Приёмка и очистка

Запусти указанную выше команду `make task` после реализации и исправления ошибок. Проверяемые случаи перечислены в соседнем `test_task.py`.

После опыта останови стенд: `docker compose -f labs/mlflow/compose.yaml down`. Не удаляй volume без экспорта истории; артефакты `work/` сохрани для следующих модулей.

## Пример корректного результата

Для сопоставимых runs с validation_mae 0.8/0.5/0.6 выбирается второй run. Изменение только test_mae не влияет на выбор. Разные data_sha256 или split вызывают ValueError, а не сравнение несопоставимых запусков.

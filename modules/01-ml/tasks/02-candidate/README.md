# Кандидат

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Редактируй `modules/01-ml/tasks/02-candidate/solution.py` (физическая заготовка рядом). Дополнительные свои тесты и `report.md` размещай в этой же папке. Полных решений в заготовке нет.

`build_pipeline(seed: int = 42) -> sklearn.pipeline.Pipeline`; `train(data: Path, output: Path, seed: int) -> None`; `main() -> None`. CLI --data --output --seed (default 42). Сравни Dummy, Ridge и небольшой RandomForest на одном split из 01-baseline; выбери конфигурацию по validation, затем один финальный test. Preprocessing fit только на train. Создай model.joblib, metrics.json, manifest.json, split.json по [контракту](../../../../labs/housing/README.md). Bundle schema_version=1, pipeline, features=FEATURES, непустой model_version. metrics: baseline/candidate × validation/test × mae/rmse. manifest: seed, data_sha256, versions, parameters, feature_order, split. Сохраняй полную модель с preprocessing; публикация атомарная, нельзя оставлять частично готовый активный bundle. Приёмка на полном housing: candidate.test.mae <= .9*baseline.test.mae. Маленький тест ниже проверяет механику, а не качество датасета.

## Среда и зависимости

Базовая среда, numpy/pandas/scikit-learn/joblib, housing; CPU.

Зависит от 01-ml/01-baseline. Эти функции являются единственной учебной реализацией для python -m housing.train. Используй course_tasks.load_task для доступа к baseline.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=01-ml/02-candidate
```

До реализации ожидается RED: `NotImplementedError`, а не ошибка импорта зависимостей. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

CLI из корня (пути аргументов относительно текущей директории; для JSONL передай полный путь к fixture):

```bash
python scripts/run_task.py run 01-ml/02-candidate -- --data work/housing.csv --output work/artifacts --seed 42
```

## Требования практического опыта

Реализуй `build_pipeline(seed)` и CLI обучения по контракту заголовка `train.py`. Сравни baseline, Ridge и небольшой RandomForestRegressor на одном split. Не подбирай параметры по test. Заверши CLI:

```bash
python -m housing.train --data work/housing.csv --output work/artifacts --seed 42
```

Ожидаются `model.joblib`, `metrics.json`, `manifest.json`, `split.json`. Порог приёмки: MAE выбранной модели на test не больше 90% MAE baseline на том же test. Если не достигнут, исследуй вход и pipeline; не меняй test ради прохождения порога. Финальное test-сравнение выполняй после выбора по validation.

## Приёмка и очистка

Пройди все тесты `test_task.py`, сохрани перечисленные артефакты и добавь объяснение решений/ограничений в `report.md`. Для инфраструктурных опытов приложи реальные команды и вывод: offline проверки не доказывают развёртывание, доступность удалённого сервера или качество объяснения. Ручная оценка: воспроизводимость шагов, соответствие исходному контракту, объяснение причины сбоя и корректное восстановление.

Docker не требуется. Временные тестовые файлы убирает pytest. Сохрани CSV, split, отчёты и модель в `work/` для следующих модулей; окружение можно завершить `deactivate`. Учебные DVC demo/remote удаляй только после экспорта результатов.

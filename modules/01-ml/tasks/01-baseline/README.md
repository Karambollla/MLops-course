# Baseline

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Редактируй `modules/01-ml/tasks/01-baseline/solution.py` (физическая заготовка рядом). Дополнительные свои тесты и `report.md` размещай в этой же папке. Полных решений в заготовке нет.

`regression_metrics(y_true, y_pred) -> dict[str,float]`: одинаковые непустые одномерные конечные массивы, иначе ValueError; ключи mae/rmse в единицах target. `make_split(n_rows: int, seed: int = 42) -> dict[str,list[int]]`: train/validation/test 60/20/20, сначала test_size=.2, затем validation_size=.25 от остатка через sklearn train_test_split с тем же seed; исходные позиционные индексы. `fit_baseline(frame, split: dict) -> dict`: проверь ровно FEATURES + TARGET, fit DummyRegressor(mean) только на train, верни validation/test mae/rmse. Сохрани split и baseline report с единицами 100000 USD.

## Среда и зависимости

Базовая среда, numpy/pandas/scikit-learn, установленный housing; CPU.

Предшественник: 00-python. Загрузи housing.csv один раз; тесты используют локальные малые таблицы.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=01-ml/01-baseline
```

До реализации ожидается RED: `NotImplementedError`, а не ошибка импорта зависимостей. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

Это задание использует функции; импортируй заготовку через `course_tasks.load_task("01-ml/01-baseline")` из Python. CLI не требуется.

## Требования практического опыта

Проверь восемь признаков из `housing.features.FEATURES`, target и отсутствие неожиданных столбцов. Создай split 60/20/20 с seed 42, сохрани индексы в JSON. На train обучи DummyRegressor. Реализуй `regression_metrics` и проверь:

```bash
RUN_EXERCISES=1 python -m pytest labs/housing/tests/test_exercises.py -v
```

Тест pipeline останется красным до задания 2. Для отдельной проверки метрик добавь `-k evaluation`. Артефакт: baseline MAE/RMSE на validation и test с единицами измерения.

## Приёмка и очистка

Пройди все тесты `test_task.py`, сохрани перечисленные артефакты и добавь объяснение решений/ограничений в `report.md`. Для инфраструктурных опытов приложи реальные команды и вывод: offline проверки не доказывают развёртывание, доступность удалённого сервера или качество объяснения. Ручная оценка: воспроизводимость шагов, соответствие исходному контракту, объяснение причины сбоя и корректное восстановление.

Docker не требуется. Временные тестовые файлы убирает pytest. Сохрани CSV, split, отчёты и модель в `work/` для следующих модулей; окружение можно завершить `deactivate`. Учебные DVC demo/remote удаляй только после экспорта результатов.

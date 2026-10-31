# Практика: ML и оценка моделей

[Теория](README.md) · [Подсказки](hints.md)

## Подготовка

```bash
python -m housing.data --output work/housing.csv
```

Заготовки: `labs/housing/src/housing/train.py`, `evaluate.py`. Данные загружаются один раз, затем практика работает локально.

## Задание 1. Baseline

Проверь восемь признаков из `housing.features.FEATURES`, target и отсутствие неожиданных столбцов. Создай split 60/20/20 с seed 42, сохрани индексы в JSON. На train обучи DummyRegressor. Реализуй `regression_metrics` и проверь:

```bash
RUN_EXERCISES=1 python -m pytest labs/housing/tests/test_exercises.py -v
```

Тест pipeline останется красным до задания 2. Для отдельной проверки метрик добавь `-k evaluation`. Артефакт: baseline MAE/RMSE на validation и test с единицами измерения.

## Задание 2. Кандидат

Реализуй `build_pipeline(seed)` и CLI обучения по контракту заголовка `train.py`. Сравни baseline, Ridge и небольшой RandomForestRegressor на одном split. Не подбирай параметры по test. Заверши CLI:

```bash
python -m housing.train --data work/housing.csv --output work/artifacts --seed 42
```

Ожидаются `model.joblib`, `metrics.json`, `manifest.json`, `split.json`. Порог приёмки: MAE выбранной модели на test не больше 90% MAE baseline на том же test. Если не достигнут, исследуй вход и pipeline; не меняй test ради прохождения порога. Финальное test-сравнение выполняй после выбора по validation.

## Задание 3. Анализ ошибок

Составь таблицу ошибок по четырём квартилям target. Проведи намеренно ошибочный опыт: обучи scaler до split и объясни утечку. Не используй этот артефакт дальше. Дополнительно сравни random split с географическим и опиши, какой вопрос отвечает каждый.

## Критерии готовности

- [ ] Baseline и кандидат сравниваются на одинаковых строках.
- [ ] Метрики и pipeline-тесты проходят, артефакты сохраняются.
- [ ] Preprocessing обучается только на train; test не участвует в подборе.
- [ ] Отчёт содержит единицы target, ограничения датасета и анализ групп.

## Завершение

Сохрани артефакты для модулей 02–05. Docker-стенд отсутствует; CSV и split не удаляй.

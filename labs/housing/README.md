# Контракт стартового проекта

Обучение и метрики — упражнения; HTTP-обвязка, загрузчик данных и тестовые примеры уже есть. Работай из корня курса, установив пакет по [SETUP](../../SETUP.md).

## Артефакты

`python -m housing.train --data work/housing.csv --output work/artifacts --seed 42` после реализации создаёт:

- `model.joblib`: словарь `schema_version=1`, `pipeline` (обученный sklearn Pipeline), `features` (точно `housing.features.FEATURES`), `model_version` (непустая строка).
- `metrics.json`: ключи `baseline` и `candidate`; у каждого `validation` и `test` с `mae`, `rmse`.
- `manifest.json`: seed, data_sha256, versions, parameters, feature_order, split.
- `split.json`: train/validation/test со списками исходных индексов строк.

Канонический порядок: MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude. Target: MedHouseVal, единица — 100000 USD. Сериализуй весь preprocessing вместе с моделью. Не загружай чужой pickle/joblib.

## HTTP

```bash
uvicorn housing.api:app --host 127.0.0.1 --port 8000
curl -i http://localhost:8000/live
curl -i http://localhost:8000/ready
curl -sS http://localhost:8000/predict -H 'Content-Type: application/json' --data-binary @labs/housing/request.json
```

`/live` возвращает 200 даже без модели; `/ready` и корректный `/predict` без модели возвращают 503. После обучения — 200. Ошибки структуры запроса — 422. Batch от 1 до 256 записей; восемь конечных чисел без дополнительных полей. Ответ: predictions, model_version, target_unit. Перестановка JSON-ключей допустима: DataFrame строится в каноническом порядке.

Неверный bundle прерывает startup. Модель загружается один раз при запуске процесса: для смены артефакта нужен перезапуск или новая выкладка. Это сознательно простой контракт для демонстрации отката.

## Тесты и заготовки

`python -m pytest labs/housing/tests -v` проверяет готовую HTTP-часть; учебные тесты пропускаются с причиной. `RUN_EXERCISES=1 python -m pytest labs/housing/tests -v` включает задания и должен падать до реализации. Добавляй собственные тесты качества и обработки артефакта; маленькая fixture в тесте pipeline не заменяет оценку California Housing.

Docker: `docker compose -f labs/housing/compose.yaml up -d --build`; остановка: та же команда с `down`. Volume с артефактами монтируется только для чтения. Без обученной модели контейнер жив, но не готов к прогнозам.

# Контракт стартового проекта

Учебный код, условия и проверки находятся в [ML-notebook](../../modules/01-ml/housing.ipynb). `housing.train` и `housing.evaluate` загружают только отмеченные ячейки с импортами и функциями из сохранённого файла, без Jupyter и выполнения остальных ячеек.

Обучение и метрики — упражнения; HTTP-обвязка, загрузчик данных и тестовые примеры уже есть. Работай из корня курса, установив пакет по [SETUP](../../SETUP.md).

## Артефакты

Последняя ячейка notebook сохраняет в `work/artifacts/`:

- `model.joblib`: словарь `schema_version=1`, `pipeline` (обученный sklearn Pipeline), `features` (точно `housing.features.FEATURES`), `model_version` (непустая строка).
- `metrics.json`: ключи `baseline` и `candidate`; у каждого `validation` и `test` с `mae`, `rmse`.
- `manifest.json`: seed, data_sha256, versions, parameters, feature_order, split.
- `split.json`: train/validation/test со списками исходных индексов строк.

Функция `save_artifacts` в последней ячейке не обучает модель. Она сохраняет подготовленные в памяти результаты; отличающиеся файлы заменяются при явном `replace=True`. API и контейнеры читают `work/artifacts/`. Для повторяемого обучения в пайплайне реализуй `train` в notebook и сохрани файл: `python -m housing.train --data work/housing.csv --output work/runs/example --seed 42`. CLI пишет тот же комплект в переданный каталог.

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

`python -m pytest labs/housing/tests -v` проверяет готовую HTTP-часть. Все проверки упражнений ML запускаются внутри notebook; `make test` их не выполняет. Маленькие синтетические данные не заменяют оценку качества на California Housing.

Docker: `docker compose -f labs/housing/compose.yaml up -d --build`; остановка: та же команда с `down`. Volume с артефактами монтируется только для чтения. Без обученной модели контейнер жив, но не готов к прогнозам.

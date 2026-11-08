# Экспорт и ONNX parity

[Модуль и подготовка](../../README.md#подготовка-к-заданиям) · [Все задания модуля](../../README.md#задания) · [Окружение курса](../../../../SETUP.md)

## Какую границу проверяет экспорт

Нужно получить из обученного Python Pipeline исполняемый ONNX-граф и убедиться, что перенос сохранил прогнозы. Наличие файла не доказывает правильность: одинаковая shape допускает перепутанные признаки. Перед работой прочитай [preprocessing и dtype](../../README.md#onnx-и-граница-preprocessing), [расчёт допуска](../../README.md#численная-проверка-переноса) и [структуру repository](../../README.md#model-repository-и-путь-запроса).

Реализуй три функции в соседнем [solution.py](solution.py). Уже предоставлены импорты SDK, [config.pbtxt](config.pbtxt) и готовый переносчик `export.py`. Вход реального экспорта — твой bundle `work/artifacts/model.joblib` с Pipeline из модуля ML. Unit-проверки матрицы и parity доступны на локальном CPU в [основном окружении](../../../../SETUP.md). Для конвертации создай отдельный Python 3.12 venv, установи `labs/triton/requirements.txt` и локальный пакет `python -m pip install --no-deps -e labs/housing`.

## Шаг 1. Восстановить порядок признаков

### `feature_matrix(rows: list[dict], feature_order: list[str]) -> np.ndarray`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `rows` | `list[dict]` | Строки с именованными числовыми признаками, без target | Собственный CSV, преобразованный в список объектов, или маленький тест | `[{"b":2,"a":1}]` |
| `feature_order` | `list[str]` | Канонический порядок столбцов выходной матрицы | Для housing — `housing.features.FEATURES` | `["a","b"]` в тесте |

Для примера результат — NumPy float32 `[[1,2]]` формы `(1,2)`. Для housing матрица имеет форму `[N,8]`, порядок: MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude. Порядок ключей объектов не задаёт порядок столбцов.

Ключи каждой строки должны точно совпадать с `feature_order`. Значения — числа, конечные и без `bool`. Пропуск, дополнительное поле, строка вместо числа или NaN/infinity дают `ValueError`. Проверь конечность и после преобразования в float32, чтобы слишком большое число не превратилось в infinity.

## Шаг 2. Сравнить два исполнения

### `parity(expected, observed, rtol=1e-4, atol=1e-5) -> dict`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `expected` | Массив или список чисел | Эталонные прогнозы формы `[N]` либо `[N,1]` | `pipeline.predict` на тех же строках | `[1.0,2.0]` |
| `observed` | Массив или список чисел | Перенесённые прогнозы с тем же N, формы `[N]` либо `[N,1]` | Результат ONNX Runtime | `[[1.0],[2.000001]]` |
| `rtol` | Число | Относительная часть допуска относительно expected | Допуск проверки экспорта | `1e-4` |
| `atol` | Число | Абсолютная часть допуска | Допуск проверки экспорта | `1e-5` |

Результат содержит `passed: bool` и `max_abs_error: float`. Для примера `passed=True`, `max_abs_error≈0.000001`. Условие сравнения разобрано в [теории](../../README.md#численная-проверка-переноса). `[1]` против `[1.5]` при стандартном допуске даёт `passed=False`. Разница чисел сама по себе не является ошибкой входа.

Неконечные значения и несовместимые формы вызывают `ValueError`. Разрешено согласовать `[N]` с `[N,1]`, но `[1,N]` или произвольное flatten/broadcasting не разрешены.

## Шаг 3. Экспортировать Pipeline и проверить граф

### `export_bundle(bundle_path: Path, output_path: Path) -> None`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `bundle_path` | `pathlib.Path` | Путь к собственному доверенному joblib bundle с Pipeline и признаками | Последняя ячейка ML-notebook, CLI `--bundle` | `Path("work/artifacts/model.joblib")` |
| `output_path` | `pathlib.Path` | Путь создаваемого ONNX-файла. Создай родительские каталоги | CLI `--output` | `Path("modules/15-triton/tasks/01-onnx/output/model.onnx")` |

Функция возвращает `None` и записывает непустой ONNX. Экспортируй весь поддерживаемый Pipeline с input `features`, `FloatTensorType([None,8])`, opset 17. `None` здесь означает изменяемую batch-ось. Используй подготовленные `convert_sklearn`, `FloatTensorType`, `onnx.checker` и `ort`. Отсутствие export-зависимостей даёт `RuntimeError` с командой установки. Не скрывай ошибки чтения bundle, конвертации или исполнения.

Проверь ONNX Runtime через `CPUExecutionProvider` на минимум 100 одинаковых строках с исходным Pipeline. До запуска подготовь `work/housing.csv` с минимум 100 строками относительно рабочего каталога: это локальный источник контрольных признаков для экспорта. Функция не имеет аргумента CSV. Сохрани её сигнатуру, а для этого сценария читай подготовленный файл и выбирай из него только `FEATURES`. Синтетический SDK-тест создаёт свой Pipeline и такой же `work/housing.csv` со 100 строками во временном рабочем каталоге. Он проверяет opset, input `features`/FP32/динамическую первую ось и совпадение прогнозов с `rtol=1e-4`, `atol=1e-5`.

## Готовый CLI и файлы

`main()` уже передаёт `--bundle` и `--output` в `export_bundle`. По умолчанию читает `work/artifacts/model.joblib`, пишет `output/model.onnx` рядом с заданием. Переданные относительные пути считаются от текущего каталога. Стандартный output вычисляется относительно самого solution.py.

[config.pbtxt](config.pbtxt) содержит серверный контракт, он не конвертирует Python-модель. Сверь его input/output names, dtype и dims с `session.get_inputs()`/`get_outputs()`. Поля config разобраны в [модуле](../../README.md#разбор-config-и-batch-dimension). Имя `variable` ожидается у converter, но проверяется по фактическому графу.

## Выполнить настоящий экспорт

Из корня курса:

```bash
python modules/15-triton/tasks/01-onnx/solution.py --bundle work/artifacts/model.joblib
make task TASK=15-triton/01-onnx
```

Python-команда вызывает твою `export_bundle`. `main()` уже разбирает пути. Успешный результат — непустой проверенный `output/model.onnx`, который принимает FP32 `[N,8]` и сохраняет прогнозы собственного Pipeline. Unit-тесты отдельно проверяют порядок, dtype и parity.

В Runtime прочитай `get_inputs()`/`get_outputs()` и сверь config: `features`/FP32/[8] на входе и фактический выход графа, ожидаемо `variable`/FP32/[1]. На тех же 100 строках проверь исходный Pipeline и Runtime с rtol=1e-4, atol=1e-5. При несовпадении исследуй порядок столбцов, dtype и preprocessing. Увеличение допуска не должно скрывать переставленные признаки.

## Передать комплект серверу

После проверки ONNX и config:

```bash
python modules/15-triton/tasks/01-onnx/export.py
```

Готовый скрипт копирует config и model.onnx в `work/triton/model_repository/housing/config.pbtxt` и `work/triton/model_repository/housing/1/model.onnx`. Проверяются только наличие и непустота файлов. Паритет, совместимость config и готовность Triton этим скриптом не проверяются.

Одинаковые файлы не меняются. Для замены отличающегося результата нужен `--replace`. Файлы заменяются атомарно по отдельности, весь комплект не является одной транзакцией. Если сервер уже работает на совместимом стенде, после замены перезапусти его:

```bash
python modules/15-triton/tasks/01-onnx/export.py --replace
docker compose -f labs/triton/compose.yaml restart triton
```

Первый запуск сервера выполняется в следующем задании. Локальный ONNX CPU-export не требует GPU. Сохрани модель, hash и metadata вне Git, config — вместе с заданием. `output/` и `work/` исключены из Git.

## Локальная проверка SDK

После реализации задания и его предшественников можно проверить ONNX-граф и ONNX Runtime на синтетических данных. Установи зависимости модуля в его окружение, затем выполни из корня курса:

```bash
MLOPS_RUN_SDK=1 python scripts/run_task.py test 15-triton/01-onnx -- -m sdk
```

Используются только временные данные, внешний сервер не нужен. Без флага проверка пропускается. При включённом флаге отсутствие SDK считается ошибкой подготовки окружения. Проверяется настоящий converter/Runtime на синтетическом Pipeline. Собственный bundle и загрузка сервера проверяются отдельно выше.

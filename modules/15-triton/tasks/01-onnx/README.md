# Экспорт и ONNX parity

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## Какую границу проверяет экспорт

Нужно получить из обученного Python Pipeline исполняемый ONNX-граф и убедиться, что перенос сохранил прогнозы. Наличие файла не доказывает правильность: одинаковая shape допускает перепутанные признаки. Перед работой прочитай [preprocessing и dtype](../../README.md#onnx-и-граница-preprocessing), [расчёт допуска](../../README.md#численная-проверка-переноса) и [структуру repository](../../README.md#model-repository-и-путь-запроса).

Уже предоставлены `solution.py`, [config.pbtxt](config.pbtxt) и готовый переносчик `export.py`. Вход реального экспорта — твой bundle `work/artifacts/model.joblib` с Pipeline из модуля ML. Unit-проверки матрицы и parity доступны на локальном CPU в [основном окружении](../../../../SETUP.md). Для конвертации создай отдельный Python 3.12 venv, установи `labs/triton/requirements.txt` и локальный пакет `python -m pip install --no-deps -e labs/housing`.

## Технический контракт

Заполни три функции в `solution.py`:

- `feature_matrix(rows,feature_order) -> numpy.ndarray` возвращает float32 матрицу `[N,F]` в заданном порядке. Ключи каждого объекта точно совпадают с feature_order; значения числовые, конечные, без bool. Пропуск, лишнее поле, NaN/infinity — ValueError.
- `parity(expected,observed,rtol=1e-4,atol=1e-5) -> dict` возвращает `passed` и `max_abs_error`. Принимает векторы `[N]` и столбцы `[N,1]` с одинаковым числом прогнозов. Не допускай случайное broadcasting; несовпадающие размеры и неконечные значения — ValueError. Численно разные конечные прогнозы дают passed=False, а не ошибку формы.
- `export_bundle(bundle_path,output_path) -> None` загружает собственный Pipeline и экспортирует input с именем `features`, shape `[None,8]`, opset 17. Создай родительскую папку output и проверь перенос на 100 одинаковых строках через ONNX Runtime.

Импорты `onnx`, ONNX Runtime (`ort`), `convert_sklearn` и `FloatTensorType` уже подготовлены в начале модуля. Проверка зависимостей сообщает, что установить для экспорта; отсутствие SDK не мешает проверять чистые функции. Подход — в [структуре заданий](../../../../docs/task-structure.md#импорты).

Проверяемый маленький пример: rows=`[{"b":2,"a":1}]`, feature_order=`["a","b"]` дают float32 `[[1,2]]` формы `(1,2)`. Expected=`[1,2]`, observed=`[[1],[2.000001]]` дают passed=True и max_abs_error≈0.000001; `[1]` против `[1.5]` даёт False. Допуск не следует увеличивать для сокрытия неверного preprocessing.

## Выполнить настоящий экспорт

Из корня курса:

```bash
python modules/15-triton/tasks/01-onnx/solution.py --bundle work/artifacts/model.joblib
make task TASK=15-triton/01-onnx
```

CLI уже разбирает `--bundle` и `--output`; стандартный выход — `output/model.onnx` рядом с заданием. Python-команда выполняет твою реализацию, а не готовый exporter. Unit-тесты проверяют порядок, dtype и parity; они не подтверждают, что собственная модель экспортирована.

Через Runtime `get_inputs()`/`get_outputs()` узнай фактические name/type/shape. Согласуй config этого задания: `features`/FP32/[8] на входе; `variable`/FP32/[1] — ожидаемый, но проверяемый выход converter. Проверь 100 строк исходным Pipeline и Runtime при rtol=1e-4, atol=1e-5, сохрани исходные прогнозы и максимальную ошибку. При несовпадении сначала исследуй порядок, dtype и граф. Проверь также, что перестановка ключей входного объекта не меняет созданную матрицу.

## Передать комплект серверу

После проверки ONNX и config:

```bash
python modules/15-triton/tasks/01-onnx/export.py
```

Готовый скрипт копирует config и model.onnx в `work/triton/model_repository/housing/config.pbtxt` и `work/triton/model_repository/housing/1/model.onnx`. Проверяются только наличие и непустота файлов. Паритет, совместимость config и готовность Triton этим скриптом не проверяются.

Одинаковые файлы не меняются; для замены отличающегося результата нужен `--replace`. Файлы заменяются атомарно по отдельности, весь комплект не является одной транзакцией. Если сервер уже работает, после замены перезапусти его на совместимом Linux-стенде:

```bash
python modules/15-triton/tasks/01-onnx/export.py --replace
docker compose -f labs/triton/compose.yaml restart triton
```

Первый запуск сервера выполняется в следующем задании; локальный ONNX CPU-export не требует GPU. Сохрани модель, hash и metadata вне Git, config — вместе с заданием. `output/` и `work/` исключены из Git. Отдельного текста для сдачи нет.

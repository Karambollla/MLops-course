# Triton HTTP SDK: запрос, readiness и численная проверка

[Модуль и подготовка](../../README.md#подготовка-к-заданиям) · [Все задания модуля](../../README.md#задания) · [Окружение курса](../../../../SETUP.md)

Табличный housing Pipeline экспортируется в ONNX заданием 01. Здесь клиент отправляет float32 tensor серверу и получает прогнозы по именам outputs. Это Triton Inference Server HTTP V2 для ONNX, без LLM API. Readiness сервера ещё не доказывает готовность модели или правильность прогноза.

## Функции и их входы

### `inference_request(rows: list[dict], feature_order: list[str], max_batch: int = 32) -> dict`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `rows` | `list[dict]` | Непустой batch объектов с числовыми признаками, без target | Собственные housing-данные или тест | `[{"b":2,"a":1},{"a":3,"b":4}]` |
| `feature_order` | `list[str]` | Канонический порядок признаков | `housing.features.FEATURES`, в тесте маленький список | `["a","b"]` |
| `max_batch` | `int` | Наибольшее разрешённое N, согласованное с config | `max_batch_size` модели | `32` |

Вызови свою `feature_matrix` из задания 01. Результат для примера:

```json
{"inputs":[{"name":"features","datatype":"FP32","shape":[2,2],"data":[1.0,2.0,3.0,4.0]}]}
```

Shape включает batch-ось, data содержит строки матрицы подряд. Пустой batch, N>max_batch или неверные признаки вызывают `ValueError`. Сеть эта функция не вызывает. [request.template.json](request.template.json) показывает структуру `[null,8]` с пустыми data: замени N и заполни N×8 чисел, прежде чем считать его рабочим запросом.

### `infer(client, rows: list[dict], feature_order: list[str], model_name="housing", output_names=("variable",), max_batch=32) -> dict[str, np.ndarray]`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | `tritonclient.http.InferenceServerClient` | Уже созданный HTTP SDK-клиент | Готовая `create_client` ниже | `create_client("http://127.0.0.1:8000")` |
| `rows` | `list[dict]` | Непустой batch признаков для прогноза | Содержимое CLI `--rows` | Одна строка восьми housing features |
| `feature_order` | `list[str]` | Порядок столбцов FP32-матрицы | `FEATURES`, CLI `--features` | `list(FEATURES)` |
| `model_name` | `str` | Имя модели в repository и URL | Имя каталога модели, CLI `--model` | `"housing"` |
| `output_names` | Последовательность `str` | Имена запрашиваемых outputs, не позиции | Metadata ONNX/Triton, CLI `--outputs` | `("variable",)` |
| `max_batch` | `int` | Максимум входных строк | Согласованное `max_batch_size` из config | `32` |

Используй настоящие `InferInput`, `set_data_from_numpy` с FP32 и binary transport, `InferRequestedOutput`, `client.infer` и `result.as_numpy(name)`. Входная матрица строится тем же `feature_matrix`, что и при экспорте. Не меняй порядок признаков между путями.

Верни словарь по именам outputs, например `{"variable": np.array([[...]], dtype=np.float32)}` для batch из одной строки. Число зависит от обученной модели. Сохрани фактическую форму ndarray. Отсутствующий output или неконечный/некорректный результат дают `ValueError`. При отсутствии SDK заготовка даёт `RuntimeError` с путём `client-requirements.txt`. Сетевые ошибки должны оставаться видимыми. Переданный client закрывает вызывающий код.

### Готовая `create_client(url, timeout=10)`

Эта функция уже реализована. Она нормализует адрес и создаёт HTTP-клиент SDK.

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `url` | `str` | Адрес сервера без пути. Допускается http(s) или host:port | CLI `--url`, затем `TRITON_URL`, затем default | `"http://127.0.0.1:8000"` |
| `timeout` | Число секунд | Одинаковый connection/network timeout SDK | Аргумент вызывающего кода | `10` |

SDK получает `url="127.0.0.1:8000"`, `ssl=False` для HTTP. Неверная схема или путь в адресе дают `ValueError`. При отсутствии SDK возникает `RuntimeError`. Используй `with create_client(...) as client`, чтобы закрыть соединения.

## Формат файла со строками

CLI `--rows` принимает путь к JSON-массиву. В одном объекте должны быть ровно восемь полей в единицах исходных данных. Target не передаётся. Пример формата одной строки из проверки клиента:

```json
[
  {
    "MedInc": 8.3,
    "HouseAge": 41,
    "AveRooms": 6.9,
    "AveBedrms": 1.0,
    "Population": 322,
    "AveOccup": 2.5,
    "Latitude": 37.8,
    "Longitude": -122.2
  }
]
```

Для собственных измерений возьми фиксированные строки своего housing CSV и сохрани их, например, в `work/triton/rows.json`. Порядок JSON-ключей может отличаться: столбцы восстанавливает `feature_matrix`.

## Готовый CLI и параметры проверок

| Аргумент или переменная | Формат и назначение | По умолчанию |
|---|---|---|
| `--rows` | Обязательный путь к JSON-списку объектов с признаками | Нет |
| `--url` / `TRITON_URL` | Адрес HTTP-сервера. Аргумент имеет приоритет над env | `http://127.0.0.1:8000` |
| `--model` | Имя загруженной модели | `housing` |
| `--features` | Имена входных колонок через пробел, в нужном порядке | Канонические `FEATURES` |
| `--outputs` | Имена outputs через пробел | `variable` |
| `TRITON_ONNX_PATH` | Путь к тому же локальному ONNX, который загружен сервером. Читается live-тестами | `work/triton/model_repository/housing/1/model.onnx` |
| `MLOPS_RUN_SDK` | `1` включает локальный тест реальных tensor/result types и ORT | Без флага тест пропущен |
| `MLOPS_RUN_INTEGRATION` | `1` разрешает live-проверки готового сервера | Без флага тесты пропущены |

CLI уже читает JSON-список строк, создаёт `InferenceServerClient`, вызывает student stub и печатает структурированный JSON: model, затем outputs с name/shape/datatype/data. Адрес берётся из `TRITON_URL` или `--url` (схема http(s) преобразуется в host:port для SDK). `--features`/`--outputs` позволяют сверить фактические имена. По умолчанию восемь канонических housing features и variable.

```bash
make task TASK=15-triton/02-server
MLOPS_RUN_SDK=1 make task TASK=15-triton/02-server
python scripts/run_task.py run 15-triton/02-server --rows work/triton/rows.json
```

rows.json содержит реальные housing строки без target. SDK устанавливается отдельно из `labs/triton/client-requirements.txt`, ONNX/ORT — из `labs/triton/requirements.txt`. Порядок окружений и ограничения платформы — в [подготовке модуля](../../README.md#подготовка-к-заданиям). `sdk`-тест вызывает твою `infer` с настоящими SDK tensor/result types и крошечным синтетическим табличным ONNX, исполняемым настоящим ORT. Подменена только граница transport. Это не Triton server и не доказательство сетевого inference. Базовая коллекция работает без SDK. Незаполненные функции остаются NotImplementedError.

На совместимом стенде после экспорта собственного ONNX:

```bash
python modules/15-triton/tasks/01-onnx/export.py
docker compose -f labs/triton/compose.yaml up -d
curl --fail -i http://127.0.0.1:8000/v2/health/ready
curl --fail -i http://127.0.0.1:8000/v2/models/housing/ready
MLOPS_RUN_INTEGRATION=1 TRITON_URL=http://127.0.0.1:8000 make task TASK=15-triton/02-server
```

Read-only HTTP probe проверяет сервер напрямую. Live-тест вызывает твою `infer` через реальный SDK client, сверяет имена/формы/конечность и все outputs с локальным ORT при rtol=1e-4/atol=1e-5. Нужен тот же ONNX, который читает сервер: `work/triton/model_repository/housing/1/model.onnx`, либо `TRITON_ONNX_PATH`. Тесты не разворачивают сервис и не создают model repository. Отсутствие SDK/runtime/модели/сервера при opt-in — ошибка, без opt-in live probes пропущены.

После проверки сохрани ONNX/hash/manifest вне Git и останови `docker compose -f labs/triton/compose.yaml down`.

# Triton HTTP SDK: запрос, readiness и численная проверка

[Теория](../../README.md) · [Практика](../../practice.md) · [Подсказки](../../hints.md)

Табличный housing Pipeline экспортируется в ONNX заданием 01. Здесь клиент отправляет float32 tensor серверу и получает прогнозы по именам outputs. Это Triton Inference Server HTTP V2 для ONNX, без LLM API. Readiness сервера ещё не доказывает готовность модели или правильность прогноза.

Сохрани чистую `inference_request(rows,feature_order,max_batch=32)`: она использует `feature_matrix` из `15-triton/01-onnx` и возвращает JSON inputs с `name=features`, `datatype=FP32`, `shape=[N,F]`, плоскими построчными data. Для `[{"b":2,"a":1},{"a":3,"b":4}]`, порядка `["a","b"]` это shape `[2,2]` и data `[1,2,3,4]`. Пустой batch, N>max_batch и неверные признаки вызывают ValueError.

Реализуй `infer(client,rows,feature_order,model_name="housing",output_names=("variable",),max_batch=32) -> dict[str,np.ndarray]`. Используй настоящие `tritonclient.http.InferInput`, `set_data_from_numpy` (FP32, binary transport), `InferRequestedOutput`, `client.infer` и `result.as_numpy(name)`. Матрица признаков общая с заданием 01; не меняй порядок столбцов. Верни каждый запрошенный output по имени, с конечными числами и реальной формой модели; отсутствующий output или некорректный результат — ValueError. SDK/сеть не заменяются выдуманными прогнозами.

CLI уже читает JSON-список строк, создаёт `InferenceServerClient`, вызывает student stub и печатает структурированный JSON: model, затем outputs с name/shape/datatype/data. Адрес берётся из `TRITON_URL` или `--url` (схема http(s) преобразуется в host:port для SDK). `--features`/`--outputs` позволяют сверить фактические имена; по умолчанию восемь канонических housing features и variable.

```bash
make task TASK=15-triton/02-server
MLOPS_RUN_SDK=1 make task TASK=15-triton/02-server
python scripts/run_task.py run 15-triton/02-server --rows work/triton/rows.json
```

rows.json содержит реальные housing строки без target. SDK устанавливается отдельно из `labs/triton/client-requirements.txt`, ONNX/ORT — из `labs/triton/requirements.txt`; порядок окружений и ограничения платформы — в практике. `sdk`-тест вызывает твою `infer` с настоящими SDK tensor/result types и крошечным синтетическим табличным ONNX, исполняемым настоящим ORT. Подменена только граница transport; это не Triton server и не доказательство сетевого inference. Базовая коллекция работает без SDK; незаполненные функции остаются NotImplementedError.

На совместимом стенде после экспорта собственного ONNX:

```bash
python modules/15-triton/tasks/01-onnx/export.py
docker compose -f labs/triton/compose.yaml up -d
curl --fail -i http://127.0.0.1:8000/v2/health/ready
curl --fail -i http://127.0.0.1:8000/v2/models/housing/ready
MLOPS_RUN_INTEGRATION=1 TRITON_URL=http://127.0.0.1:8000 make task TASK=15-triton/02-server
```

Старый read-only HTTP probe сохранён; новый live-тест дополнительно вызывает твою `infer` через реальный SDK client, сверяет имена/формы/конечность и все outputs с локальным ORT при rtol=1e-4/atol=1e-5. Нужен тот же ONNX, который читает сервер: `work/triton/model_repository/housing/1/model.onnx`, либо `TRITON_ONNX_PATH`. Тесты не разворачивают сервис и не создают model repository. Отсутствие SDK/runtime/модели/сервера при opt-in — ошибка, без opt-in live probes пропущены.

После проверки сохрани ONNX/hash/manifest вне Git и останови `docker compose -f labs/triton/compose.yaml down`.

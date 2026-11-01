# Triton: запрос и готовность модели

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## Почему readiness недостаточно

Сервер может принимать HTTP, пока нужная модель не загрузилась. Даже готовая модель может получать неверно сформированный tensor. Здесь нужно собрать запрос HTTP V2 и проверить ответ на тех же входах, что локальный ONNX Runtime. Разбор [batch dimension](../../README.md#разбор-config-и-batch-dimension) и [готовности](../../README.md#http-v2-и-готовность) объясняет эти разные границы.

Уже должны быть реализованы `feature_matrix` и ONNX-export предыдущего задания. Запусти его `export.py`: Compose читает только `work/triton/model_repository/housing/config.pbtxt` и `1/model.onnx`, а не файлы в каталоге задания. Предоставлены `solution.py` и `request.template.json`. Шаблон с null/пустым data не является отправляемым запросом.

Чистое формирование JSON проверяется на локальном CPU в [основном окружении](../../../../SETUP.md). Реальный сервер — дополнительный Linux x86_64 CPU-стенд образа 25.06-py3 с `KIND_CPU`; GPU не используется. Совместимость образа с ARM64 не предполагается.

## Технический контракт

Реализуй `inference_request(rows,feature_order,max_batch=32) -> dict`, используя `feature_matrix` из `15-triton/01-onnx` через `load_task`. Результат содержит `inputs` с одним объектом: `name:"features"`, `datatype:"FP32"`, `shape:[N,F]`, `data` — плоский список чисел построчно после преобразования к float32. Пустой batch или N>max_batch вызывает ValueError; ошибки признаков не должны скрываться.

Для rows=`[{"b":2,"a":1},{"a":3,"b":4}]` и feature_order=`["a","b"]` корректны shape=`[2,2]`, data=`[1.0,2.0,3.0,4.0]`. Это пример универсальной функции, а housing-запрос использует F=8. Объём данных должен равняться произведению размеров shape. Batch-ось входит в shape запроса, но не в dims `[8]` config при max_batch_size>0.

## Проверить сервер и inference

Из корня курса на совместимом стенде:

```bash
docker compose -f labs/triton/compose.yaml up -d
curl --fail -i http://127.0.0.1:8000/v2/health/ready
curl --fail -i http://127.0.0.1:8000/v2/models/housing/ready
curl --fail http://127.0.0.1:8000/v2/models/housing
```

Первый endpoint проверяет сервер, второй — модель, третий показывает metadata. Отправь результат своей функции с реальной строкой восьми признаков в `/v2/models/housing/infer`. Ожидаются именованные выходы с конечными числами и теми shapes, которые описаны ONNX. Правильного универсального прогноза нет: он зависит от твоего Pipeline.

```bash
make task TASK=15-triton/02-server
MLOPS_RUN_INTEGRATION=1 TRITON_URL=http://127.0.0.1:8000 make task TASK=15-triton/02-server
```

Первая команда вызывает функцию тестами, CLI нет. Вторая проверяет readiness, отправляет реальный inference и сравнивает все outputs по имени с локальным ONNX Runtime на тех же FP32-входах при rtol=1e-4/atol=1e-5. Нужны Runtime и тот же файл `work/triton/model_repository/housing/1/model.onnx`, который загружен сервером; иной путь задаёт `TRITON_ONNX_PATH`.

Probe ничего не скачивает, не экспортирует и не разворачивает. Без opt-in он пропущен, с opt-in отсутствие файла/runtime/сервера — ошибка. Если readiness не проходит, проверь logs и repository; если не совпали числа — сначала hash реально загруженного ONNX и входы. [Диагностика](../../README.md#платформы-и-диагностика) разделяет ошибки загрузки и неверные прогнозы.

## Завершение

Сохрани проверенный комплект модели и metadata, затем выполни `docker compose -f labs/triton/compose.yaml down`. Реальный успешный запрос подтверждает этот контракт; он ещё не является сравнением производительности.

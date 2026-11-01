# Triton: запрос и готовность модели

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## С чего начать

Реализуй `inference_request(rows, feature_order, max_batch=32)`: вернуть inputs=[{name:"features", datatype:"FP32", shape:[N,F], data:[плоский список float32]}]. Используй feature_matrix предыдущего задания через load_task. Пустой/слишком большой batch — ValueError. Затем отправь этот запрос реальному серверу, проверив и server readiness, и readiness модели. `request.template.json` поясняет wire-shape, а не является готовым прогнозом.

Подготовь [основное окружение](../../../../SETUP.md). Все команды ниже выполняются из корня курса. Платформа задания: **linux-x86_64**. Функции и ожидаемые результаты описаны также в `test_task.py`; тесты используют небольшие фиксированные данные.

## Исходное задание

Сначала выполни `export.py` предыдущего задания: в `work/triton/model_repository/housing/` должны находиться `config.pbtxt` и `1/model.onnx`. Compose монтирует этот каталог только для чтения. Без переноса результата модель не будет готова.

```bash
docker compose -f labs/triton/compose.yaml up -d
curl -i http://localhost:8000/v2/health/ready
curl -i http://localhost:8000/v2/models/housing/ready
```

Отправь inference в `/v2/models/housing/infer` с input features, datatype FP32 и shape [1,8]. Проверь имя output по метаданным. Без созданного ONNX model repository неполон, поэтому успешная готовность не ожидается.

## Проверка

```bash
make task TASK=15-triton/02-server
```

У этой задачи проверяются функции: запускай их тестами, отдельного CLI нет.

До реализации функции ожидается `NotImplementedError`. Реализуй заготовку, сохраняя контракт функций из тестов. Офлайн-тест не подтверждает действия на внешнем стенде: проверки, требующие работающего сервиса, включаются явно через `MLOPS_RUN_INTEGRATION=1`.

## Результат

Функции должны проходить проверки положительных и отрицательных случаев. Для собственного эксперимента сохраняй исходные измерения в `work/`: они пригодятся для повторного сравнения. Отдельное письменное резюме не требуется. После работы останови стенд по инструкции practice.md.

### Проверка реального inference

```bash
MLOPS_RUN_INTEGRATION=1 TRITON_URL=http://127.0.0.1:8000 make task TASK=15-triton/02-server
```

Probe читает readiness, отправляет inference и сравнивает все outputs с локальным ONNX Runtime на тех же FP32-входах. Требуются установленный ONNX Runtime и тот же файл `work/triton/model_repository/housing/1/model.onnx`, который загружен сервером. Другой путь можно передать через `TRITON_ONNX_PATH`. Сам probe ничего не экспортирует, не скачивает и не разворачивает.

Ожидаются HTTP 200, конечные числа и совпадение с локальным ONNX при rtol=1e-4, atol=1e-5. Конкретный прогноз зависит от твоей модели; готового «правильного числа» здесь нет. Без opt-in probe пропускается; при включении отсутствие runtime, файла или сервера — ошибка.

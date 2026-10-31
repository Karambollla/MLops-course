# Практика: Triton Inference Server и перенос модели

[Теория](README.md) · [Подсказки](hints.md)

## Основной путь: Mac

Создай отдельное окружение, установи `labs/triton/requirements.txt` и housing с --no-deps. Реализуй `labs/triton/export.py`: экспорт с именем input features и opset 17; сохрани модель в `labs/triton/model_repository/housing/1/model.onnx`.

```bash
python labs/triton/export.py
```

Через ONNX Runtime узнай фактические output name/shape и согласуй config.pbtxt. Проверь parity на 100 строках и сохрани максимальную абсолютную ошибку. Добавь тест перестановки признаков: preprocessing обязан восстановить канонический порядок до создания массива.

## Дополнительный путь: Linux x86_64

```bash
docker compose -f labs/triton/compose.yaml up -d
curl -i http://localhost:8000/v2/health/ready
curl -i http://localhost:8000/v2/models/housing/ready
```

Отправь inference в `/v2/models/housing/infer` с input features, datatype FP32 и shape [1,8]. Проверь имя output по метаданным. Без созданного ONNX model repository неполон, поэтому успешная готовность не ожидается.

## Измерения

Сравни один и тот же набор строк в FastAPI и Triton. Прогрей модель, затем выполни минимум 200 запросов при concurrency 1 и 4; запиши p50/p95, throughput, ошибки, batch и ресурсы. Если Triton не запускался, сохрани только локальный parity и план бенчмарка — без выдуманных цифр.

## Критерии готовности

- [ ] ONNX parity проходит с указанным допуском.
- [ ] Input/output config согласованы с фактической моделью.
- [ ] Batch dimension объяснена на одном и нескольких объектах.
- [ ] Статус runtime-части явно указан.

## Завершение

Triton: `docker compose -f labs/triton/compose.yaml down`. Сохрани ONNX вне Git вместе с hash/manifest. Для основного Mac-пути деактивируй отдельный venv.

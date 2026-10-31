# 15. Triton Inference Server и перенос модели

[Программа](../../README.md) · [Практика](practice.md) · [Подсказки](hints.md)

## Цель и вход

Экспортировать собственную модель, проверить численный результат в ONNX Runtime и понять контракт специализированного сервера. Нужен обученный Pipeline. Triton Inference Server — сервер обслуживания моделей NVIDIA; язык Triton для GPU kernels — другой проект и не является предметом этой лабораторной.

## Backend и model repository

Triton принимает HTTP/gRPC-запросы и передаёт вычисления backend: ONNX Runtime, TensorRT, Python и другим поддерживаемым вариантам. Сервис предоставляет управление версиями, batching, метрики и настройки instances. Он не делает любую модель автоматически быстрее: это нужно измерить для конкретного batch, hardware и нагрузки.

Model repository содержит директорию модели, config.pbtxt и нумерованные версии, например housing/1/model.onnx. Имя input/output, dtype и shape в config должны совпадать с самим ONNX. Номер директории Triton не обязан совпадать с MLflow model version; связь фиксируется release manifest.

## ONNX и preprocessing

ONNX описывает граф вычислений. Экспорт поддерживается не для каждого sklearn estimator и преобразования. Если preprocessing не вошёл в граф, клиент обязан воспроизвести его точно — это дополнительный источник training-serving skew. Предпочитай экспорт всего поддерживаемого Pipeline и проверяй operators/opset.

У input в упражнении shape `[None, 8]`, dtype float32. Случайный DataFrame с неправильным порядком столбцов будет иметь допустимую shape, но неверный смысл. Сначала расположи признаки по FEATURES, затем преобразуй в float32.

Проверь результат ONNX Runtime против исходного Pipeline минимум на 100 строках с `rtol=1e-4`, `atol=1e-5`. Если допуск не проходит, исследуй converter, dtype и operators; не увеличивай допуск до произвольного числа без объяснения.

## Batch dimension

В Triton при max_batch_size > 0 batch dimension не включается в dims отдельных tensors в config. Для восьми признаков dims=[8], а реальный запрос имеет shape=[batch,8]. Если max_batch_size=0, shape трактуется иначе. Неправильное понимание этой границы часто даёт mismatch ещё до вычисления.

Dynamic batching объединяет независимые запросы, чтобы эффективнее использовать вычисления. Ожидание сборки batch повышает отдельную latency, но может увеличить throughput. Сравни batch=1 и несколько запросов при разных уровнях concurrency, не делая вывод только по одному прогретому запросу.

## CPU и NVIDIA

ONNX Runtime на Mac ARM64 — обязательная локальная часть. Закреплённый Triton image в этой лабораторной рассматривается как дополнительный Linux x86_64 стенд. CPU backend не требует запускать GPU, но архитектура и состав image всё равно должны подходить машине. TensorRT backend и TensorRT-LLM требуют совместимой NVIDIA-среды.

Triton readiness, readiness конкретной модели и успешный inference — отдельные проверки. Метрики на 8002 не заменяют измерение клиентской end-to-end latency. Для реального сравнения FastAPI и Triton укажи одинаковые данные, batch, concurrency, warmup и hardware.

## Материалы

Все ссылки отобраны 2026-10-31; статус HTTP-проверки — в [отчёте](../../docs/verification.md).

- [Triton architecture](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/architecture.html) — backend, scheduler и model instances.
- [Model configuration](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_configuration.html) — dims, batch и input/output.
- [skl2onnx tutorial](https://onnx.ai/sklearn-onnx/) — поддерживаемые converters и initial_types.
- [ONNX Runtime Python](https://onnxruntime.ai/docs/get-started/with-python.html) — InferenceSession и локальная проверка.

# Подсказки: Triton Inference Server и перенос модели

[Вернуться к заданиям](practice.md)

Открывай следующий пункт только после собственной попытки.

1. `FloatTensorType([None, 8])` задаёт экспортируемый input. Имя features должно совпасть с config.
2. Узнай output через `session.get_outputs()`; variable — ожидаемое имя converter, но проверять его нужно фактически.
3. ONNX Runtime принимает NumPy float32, а не произвольный JSON. Перед преобразованием упорядочь столбцы.
4. В config dims не включают batch при max_batch_size > 0. Пример shape [1,8] содержит один объект.
5. После проверки ONNX выполни `python modules/15-triton/tasks/01-onnx/export.py`. В `work/triton/model_repository/housing/` должны быть config.pbtxt и 1/model.onnx. Пустая папка версии — заготовка, а не рабочая модель.

6. SDK `InferInput` описывает полный tensor `[N,F]` и FP32; `set_data_from_numpy` отправляет данные массива. `InferRequestedOutput` и `as_numpy` используют **имя** output, а не позицию списка.
7. `InferenceServerClient` ждёт host:port; CLI уже разбирает схему `TRITON_URL`. Прогноз из CLI содержит named outputs; сверяй dtype/shape и численное совпадение с ORT, а не только HTTP 200.
8. В benchmark нужны отдельные отметки времени для каждого запроса и всей серии. Warmup не входит ни в samples, ни в elapsed. Статус 500 здесь отмечает ошибку клиента без сохранения тела/текста ошибки.
9. Для четырёх потоков нужны независимые SDK clients: HTTP client не thread safe. Тесты с transport double подтверждают контракт типов; реальный server probe включается отдельно.

## Самопроверка

Что не умеет converter? Чем server readiness отличается от model readiness? Почему batching может ухудшить одиночную latency? Чем Triton Server отличается от языка Triton?

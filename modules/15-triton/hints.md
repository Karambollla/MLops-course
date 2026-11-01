# Подсказки: Triton Inference Server и перенос модели

[Вернуться к заданиям](practice.md)

Открывай следующий пункт только после собственной попытки.

1. `FloatTensorType([None, 8])` задаёт экспортируемый input. Имя features должно совпасть с config.
2. Узнай output через `session.get_outputs()`; variable — ожидаемое имя converter, но проверять его нужно фактически.
3. ONNX Runtime принимает NumPy float32, а не произвольный JSON. Перед преобразованием упорядочь столбцы.
4. В config dims не включают batch при max_batch_size > 0. Пример shape [1,8] содержит один объект.
5. После проверки ONNX выполни `python modules/15-triton/tasks/01-onnx/export.py`. В `work/triton/model_repository/housing/` должны быть config.pbtxt и 1/model.onnx. Пустая папка версии — заготовка, а не рабочая модель.

## Самопроверка

Что не умеет converter? Чем server readiness отличается от model readiness? Почему batching может ухудшить одиночную latency? Чем Triton Server отличается от языка Triton?

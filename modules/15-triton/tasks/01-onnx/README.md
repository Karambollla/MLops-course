# Экспорт и ONNX parity

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## С чего начать

Реализуй `feature_matrix(rows, feature_order) -> numpy.ndarray` float32 [N,F]: ключи каждого объекта точно совпадают с feature_order, значения конечные числовые без bool. `parity(expected, observed, rtol=1e-4, atol=1e-5) -> dict` возвращает passed и max_abs_error; допускаются [N] и [N,1], несовпадающие размеры/NaN — ValueError. `export_bundle(bundle_path, output_path)` экспортирует собственный Pipeline с input features и opset17. ONNX SDK импортируется внутри этой функции как необязательная зависимость. Unit-тесты матрицы и parity доступны в основном окружении; реальный export требует requirements Triton.

Подготовь [основное окружение](../../../../SETUP.md). Все команды ниже выполняются из корня курса. Платформа задания: **cpu**. Функции и ожидаемые результаты описаны также в `test_task.py`; тесты используют небольшие фиксированные данные.

## Исходное задание

Создай отдельное окружение, установи `labs/triton/requirements.txt` и housing с --no-deps. Реализуй `modules/15-triton/tasks/01-onnx/solution.py`: экспорт с именем input features и opset 17; сохрани модель в `labs/triton/model_repository/housing/1/model.onnx`.

```bash
python modules/15-triton/tasks/01-onnx/solution.py
```

Через ONNX Runtime узнай фактические output name/shape и согласуй config.pbtxt. Проверь parity на 100 строках и сохрани максимальную абсолютную ошибку. Добавь тест перестановки признаков: preprocessing обязан восстановить канонический порядок до создания массива.

## Проверка

```bash
make task TASK=15-triton/01-onnx
```

Для Python CLI:

```bash
python scripts/run_task.py run 15-triton/01-onnx -- --help
```

До реализации функции ожидается `NotImplementedError`; для отчётов — ошибка незаполненного поля. Исправляй заготовку или собственный результат, сохраняя ожидаемое поведение тестов. Офлайн-тест не подтверждает действия на внешнем стенде: проверки, требующие работающего сервиса, включаются явно через `MLOPS_RUN_INTEGRATION=1`.

## Критерии и завершение

Покажи результаты исходного задания и объясни позитивные и негативные случаи из тестов. Сохрани собственные измерения и команды в work/. Затем останови стенд по общей инструкции practice.md модуля.

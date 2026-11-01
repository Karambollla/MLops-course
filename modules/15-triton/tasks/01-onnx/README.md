# Экспорт и ONNX parity

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## С чего начать

Реализуй `feature_matrix(rows, feature_order) -> numpy.ndarray` float32 [N,F]: ключи каждого объекта точно совпадают с feature_order, значения конечные числовые без bool. `parity(expected, observed, rtol=1e-4, atol=1e-5) -> dict` возвращает passed и max_abs_error; допускаются [N] и [N,1], несовпадающие размеры/NaN — ValueError. `export_bundle(bundle_path, output_path)` экспортирует собственный Pipeline с input features и opset17. ONNX SDK импортируется внутри этой функции как необязательная зависимость. Unit-тесты матрицы и parity доступны в основном окружении; реальный export требует requirements Triton.

Подготовь [основное окружение](../../../../SETUP.md). Все команды ниже выполняются из корня курса. Платформа задания: **cpu**. Функции и ожидаемые результаты описаны также в `test_task.py`; тесты используют небольшие фиксированные данные.

## Исходное задание

Создай отдельное окружение, установи `labs/triton/requirements.txt` и housing с --no-deps. Реализуй `modules/15-triton/tasks/01-onnx/solution.py`: экспорт с именем input features и opset 17. Стандартный выход CLI — `output/model.onnx` рядом с заготовкой; создай родительскую папку в своей реализации.

```bash
python modules/15-triton/tasks/01-onnx/solution.py
```

Через ONNX Runtime узнай фактические output name/shape и согласуй [config.pbtxt](config.pbtxt) в этой папке задания. Проверь parity на 100 строках и сохрани максимальную абсолютную ошибку. Добавь тест перестановки признаков: preprocessing обязан восстановить канонический порядок до создания массива.

## Передача модели Triton

После проверки ONNX и конфигурации запусти готовый скрипт:

```bash
python modules/15-triton/tasks/01-onnx/export.py
```

Он копирует `config.pbtxt` и `output/model.onnx` в `work/triton/model_repository/housing/config.pbtxt` и `work/triton/model_repository/housing/1/model.onnx`. Этот model repository монтируется Compose-стендом следующего задания. Скрипт не запускает решение, ONNX Runtime или Triton; он проверяет только наличие непустых файлов. Совместимость конфигурации и parity проверяй самостоятельно.

Одинаковые файлы не меняются; при другом существующем результате требуется `--replace`. Скрипт работает из любой директории при вызове по абсолютному пути. Конфигурация переносится перед моделью; каждый файл заменяется атомарно, но комплект не является одной транзакцией. После замены перезапусти Triton:

```bash
python modules/15-triton/tasks/01-onnx/export.py --replace
docker compose -f labs/triton/compose.yaml restart triton
```

Первый запуск сервера выполняется в следующем задании на совместимой платформе. `output/` и `work/` исключены из Git; редактируемый `config.pbtxt` сохраняется вместе с заданием.

## Проверка

```bash
make task TASK=15-triton/01-onnx
```

Для Python CLI:

```bash
python scripts/run_task.py run 15-triton/01-onnx -- --help
```

До реализации функции ожидается `NotImplementedError`. Реализуй заготовку, сохраняя контракт функций из тестов. Офлайн-тест не подтверждает действия на внешнем стенде: проверки, требующие работающего сервиса, включаются явно через `MLOPS_RUN_INTEGRATION=1`.

## Результат

Функции должны проходить проверки положительных и отрицательных случаев. Для собственного эксперимента сохраняй исходные измерения в `work/`: они пригодятся для повторного сравнения. Отдельное письменное резюме не требуется. После работы останови стенд по инструкции practice.md.

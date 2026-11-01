# Кандидат

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Зачем сохранять весь путь прогноза

Из [baseline](../01-baseline/README.md) уже известны правила split и оценки. Теперь нужна полезная модель, которую можно вызвать вне процесса обучения. Отдельно сохранённые коэффициенты без scaler и порядка признаков не гарантируют тот же прогноз в API. Поэтому результатом становится Pipeline внутри bundle и метаданные его получения. Перед работой прочти [Pipeline и модели](../../README.md#pipeline-и-модели) и [контракт файлов обучения](../../README.md#что-сохраняет-программа-обучения).

## Исходные файлы и ответственность заготовки

На входе собственный `work/housing.csv`, реализованные `make_split`, `fit_baseline` и `regression_metrics`. В заготовке уже есть разбор `--data`, `--output`, `--seed`; реализовать нужно `build_pipeline` и `train`. Адаптер `housing.train` вызывает именно этот код. Повторно писать метрики или скрытую вторую реализацию обучения в другом месте не нужно.

Для проверки механики маленький тест обучает на синтетической таблице, сохраняет модель, загружает её и сравнивает прогнозы. Это не подтверждает качество на housing. Для полного опыта, например, при baseline test MAE=0.80 кандидат с 0.70 проходит границу `0.9*0.80=0.72`; кандидат с 0.75 не проходит. Числа иллюстративные. Выбрать конфигурацию нужно до этой test-проверки, по validation. Выходные четыре файла должны относиться к одному обучению, а `manifest.split` совпадать с `split.json`.

## Где работать и контракт

Редактируй `modules/01-ml/tasks/02-candidate/solution.py`. Дополнительные тесты размещай в этой же папке.

`build_pipeline(seed: int = 42) -> sklearn.pipeline.Pipeline`; `train(data: Path, output: Path, seed: int) -> None`; `main() -> None`. CLI --data --output --seed (default 42). Сравни Dummy, Ridge и небольшой RandomForest на одном split из 01-baseline; выбери конфигурацию по validation, затем один финальный test. Preprocessing fit только на train. Создай model.joblib, metrics.json, manifest.json, split.json по [контракту](../../../../labs/housing/README.md). Bundle schema_version=1, pipeline, features=FEATURES, непустой model_version. metrics: baseline/candidate × validation/test × mae/rmse. manifest: seed, data_sha256, versions, parameters, feature_order, split. Сохраняй полную модель с preprocessing; публикация атомарная, нельзя оставлять частично готовый активный bundle. Приёмка на полном housing: candidate.test.mae <= .9*baseline.test.mae. Маленький тест ниже проверяет механику, а не качество датасета.

## Среда и зависимости

Базовая среда, numpy/pandas/scikit-learn/joblib, housing; CPU.

Зависит от 01-ml/01-baseline. Эти функции являются единственной учебной реализацией для python -m housing.train. Используй course_tasks.load_task для доступа к baseline.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=01-ml/02-candidate
```

Тесты функций работают offline на маленьких входах и временных файлах. До реализации ожидается `NotImplementedError`; ошибка импорта означает проблему подготовки среды. Проверка функций не заменяет описанный опыт на данных или стенде.

CLI из корня; результат обучения сохраняется в `output/` этого задания:

```bash
python scripts/run_task.py run 01-ml/02-candidate -- --data work/housing.csv --output modules/01-ml/tasks/02-candidate/output --seed 42
```

## Требования практического опыта

Реализуй `build_pipeline(seed)` и CLI обучения по контракту заголовка `train.py`. Сравни baseline, Ridge и небольшой RandomForestRegressor на одном split. Не подбирай параметры по test. Заверши CLI:

```bash
python -m housing.train --data work/housing.csv --output modules/01-ml/tasks/02-candidate/output --seed 42
```

Ожидаются `model.joblib`, `metrics.json`, `manifest.json`, `split.json`. Порог приёмки: MAE выбранной модели на test не больше 90% MAE baseline на том же test. Если не достигнут, исследуй вход и pipeline; не меняй test ради прохождения порога. Финальное test-сравнение выполняй после выбора по validation.

## Передача результата следующим модулям

После обучения и проверки качества запусти готовый скрипт:

```bash
python modules/01-ml/tasks/02-candidate/export.py
```

Он проверит наличие четырёх непустых файлов и синтаксис JSON, затем скопирует комплект из `output/` в `work/artifacts/`. Он не запускает решение, не загружает модель и не проверяет её качество. API, Docker и следующие модули используют этот каталог без дополнительного копирования.

Совпадающие файлы не меняются. Если в `work/artifacts/` уже другой результат, скрипт перечислит конфликты и завершится без переноса. Для осознанной замены:

```bash
python modules/01-ml/tasks/02-candidate/export.py --replace
```

Модель заменяется последней; каждый файл заменяется атомарно, но весь комплект не является одной транзакцией. После замены перезапусти API. `output/` и `work/` исключены из Git; экспортёр и шаблоны остаются в репозитории. Сам экспортёр работает из любой директории при вызове по абсолютному пути.

## Приёмка и очистка

Запусти указанную выше команду `make task` после реализации и исправления ошибок. Проверяемые случаи перечислены в соседнем `test_task.py`.

Docker не требуется. Временные тестовые файлы убирает pytest. Сохрани CSV, split и корректный комплект обучения для модуля воспроизводимости; окружение можно завершить `deactivate`.

## Пример корректного результата

В output/ созданы model.joblib, metrics.json, manifest.json, split.json. Повторный запуск на тех же данных и seed даёт одинаковый split и прогнозы в допуске. На полном датасете candidate.test.mae не больше 0.9 × baseline.test.mae; unit-тесты на маленькой fixture не заменяют эту проверку качества.

# Манифест и контракт

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Редактируй `modules/02-reproducibility/tasks/02-manifest/solution.py` (физическая заготовка рядом). Дополнительные тесты размещай в этой же папке. Полных решений в заготовке нет.

`build_manifest(data_path: Path, seed: int, split: dict, versions: dict, parameters: dict) -> dict` включает schema_version=1, seed, data_sha256, split, versions, parameters, feature_order=FEATURES. `validate_bundle(bundle: dict, manifest: dict, expected_sha256: str) -> None` проверяет schema_version=1, pipeline с callable predict, точный features/feature_order и data_sha256, непустой model_version; несовместимость — ValueError. Подключи эти функции к train задания 01-ml/02-candidate. Допиши происхождение: Git commit, либо явное отсутствие Git и checksum исходников; источник CSV, дата, единицы и ограничения. Не сохраняй секреты и абсолютные обязательные пути ноутбука.

## Среда и зависимости

Базовая среда из SETUP: Python, pytest; CPU, Linux/macOS.

Зависит от 01-ml/02-candidate и 02-reproducibility/01-data-version. Два реальных запуска сравниваются в следующем задании; bundle загружай только собственный.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=02-reproducibility/02-manifest
```

До реализации ожидается RED: `NotImplementedError`, а не ошибка импорта зависимостей. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

Это задание использует функции; импортируй заготовку через `course_tasks.load_task("02-reproducibility/02-manifest")` из Python. CLI не требуется.

## Требования практического опыта

Доработай train CLI: `manifest.json` содержит seed, хеш CSV, split, версии, параметры и список признаков. Bundle `model.joblib` — словарь с ключами `schema_version=1`, `pipeline`, `features`, `model_version`; точные требования есть в [контракте](../../../../labs/housing/README.md). Сделай два запуска с одинаковыми входами и сравни прогнозы на фиксированных 20 строках через `numpy.allclose` с `rtol=1e-6`, `atol=1e-8`.

## Приёмка и очистка

Выполни `test_task.py`: проверяются результаты функций, ошибки входа и изменения технических артефактов. Письменный пересказ выполнения не требуется.

Docker не требуется. Временные тестовые файлы убирает pytest. Сохрани необходимые CSV, split и модель для следующих модулей; окружение можно завершить `deactivate`. Учебные DVC demo/remote удаляй только после экспорта результатов.

## Пример корректного результата

Для собственного bundle с правильной схемой и SHA проверка завершается без исключения. Перестановка features, другой data_sha256 или пустой model_version приводят к ValueError до predict. Манифест не меняется при последующем изменении переданного исходного dict.

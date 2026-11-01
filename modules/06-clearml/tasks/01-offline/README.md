# ClearML: реальное offline обучение

Реализуй `train_and_log(task, data_path, output_dir, seed=42)` в `solution.py`.
Вызови `housing.train.train(data_path, output_dir, seed)` из собственного модуля 01.
Прочитай полученные metrics.json и manifest.json: `task.connect` получает seed и
SHA256 CSV; `task.get_logger().report_scalar` — title="quality", series="mae"/"rmse",
реальные candidate.test метрики, iteration=0. Через `task.upload_artifact` загрузи
файлы с именами model.joblib и manifest.json. Ошибки обучения должны распространяться.
Возвращаемое значение не оценивается. `main()` уже закрывает Task в finally.

Команды из корня репозитория, CPU-окружение [SETUP](../../../../SETUP.md),
завершённые модули 01–03. Для тестов SDK не нужен:

```bash
python -m pytest modules/06-clearml/tasks/01-offline/test_task.py -q
```

После реализации ожидаются 4 passed; до реализации — NotImplementedError.
Тесты подменяют только обучение и SDK: проверяют вызовы твоей функции на разных
выходах обучения, а не качество модели или наличие настоящей offline-сессии.

Реальная практика (установи `labs/clearml/requirements.txt` в отдельное окружение):

```bash
CLEARML_OFFLINE_MODE=1 python modules/06-clearml/tasks/01-offline/solution.py --data work/housing.csv --output modules/06-clearml/tasks/01-offline/output --seed 42
find modules/06-clearml/tasks/01-offline/output -maxdepth 1 -type f
```

Иллюстрация результата: SDK печатает путь offline session; output содержит
model.joblib, metrics.json, manifest.json, split.json. В SDK-сессии есть те же
MAE/RMSE и два непустых артефакта. Путь cache зависит от SDK-конфигурации.
Это локальный tracking; очередь и remote execution проверяются в следующем задании.
Отчёт и письменное описание не требуются. Сохрани свой cache для импорта;
временный output можно удалить после использования. Credentials в Git не добавляй.

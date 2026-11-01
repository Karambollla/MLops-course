# ClearML: сравнение и отказ

Нужны завершённые 04-mlflow и 06-clearml/01-offline; agent-ветка использует 02-agent.
Сравни один CSV/hash, seed, split и pipeline в MLflow и ClearML. Проверяй реальные
metrics/artifacts в UI: MAE/RMSE должны совпасть в пределах погрешности повторного
обучения. Сопоставь tracking (MLflow/ClearML), schedule (Airflow), execution (agent).
Обдумай стоимость сопровождения и доступность данных; письменная таблица не нужна.

```bash
curl --fail --max-time 10 http://127.0.0.1:5001/health
CLEARML_OFFLINE_MODE=1 python modules/06-clearml/tasks/01-offline/solution.py --data work/housing.csv --output modules/06-clearml/tasks/03-comparison-failure/output --seed 42
```

Иллюстрация: health возвращает успешный статус; ClearML пишет путь session;
в обеих системах совпадают seed/hash и содержимое model/manifest.

Для offline отказа временно введи `raise RuntimeError("injected training failure")`
в свою функцию обучения перед публикацией модели; запусти ту же CLI с новым output.

```bash
CLEARML_OFFLINE_MODE=1 python modules/06-clearml/tasks/01-offline/solution.py --data work/housing.csv --output modules/06-clearml/tasks/03-comparison-failure/failed-output --seed 42
echo $?
```

Ожидается ненулевой exit и исключение injected training failure; `finally` закрывает
Task, SDK сохраняет offline-сессию. Не публикуй частичную модель как готовую.
Убери инъекцию и повтори с новым output: exit 0, настоящие metrics/artifacts.
Если проверяешь agent: отправь отдельный клон задачи, дождись in_progress,
останови своего agent Ctrl+C, посмотри статус в UI, затем возобнови или повтори
задачу. Состояние после отказа зависит от таймаутов и версии; не выдавай ожидаемый
статус за измеренный. Проверяй разные Task IDs и риск дубликатов/run_key.
Автоматическая аттестация этих переходов не предлагается.

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы ниже иллюстрируют инварианты; это не запись успешного выполнения.
Отчёт, JSON-подтверждение и письменное описание не требуются.
[Теория](../../README.md) · [Подсказки](../../hints.md)

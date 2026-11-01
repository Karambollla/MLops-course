# Сбой и интервалы

[Практика модуля](../../practice.md) · [Теория](../../README.md) · [Подсказки](../../hints.md) · [SETUP](../../../../SETUP.md)

## Где работать и контракт

Редактируй `modules/05-airflow/tasks/03-failure-intervals/solution.py` (физическая заготовка рядом). Дополнительные свои тесты и `report.md` размещай в этой же папке. Полных решений в заготовке нет.

`interval_manifest(start: str, end: str) -> dict`: ISO 8601 aware datetime, end>start, ровно 24 часа в UTC, иначе ValueError. Верни data_interval_start/data_interval_end в UTC с +00:00 и partition=дата UTC начала. Никакого now(). `resume_publish(state: dict, publish_fn) -> dict`: state={run_key, artifact_path, status:"evaluated"|"published", interval:{...}}; для evaluated вызывает callback(state), возвращающий release dict, затем возвращает копию state со status=published и release. Ошибка callback пробрасывается, вход не мутируется; для published callback не вызывается. Это возобновление после сбоя непосредственно перед publish; callback использует идемпотентный publish предыдущего задания для окна после внешнего side effect. В DAG добавь ежедневное UTC расписание, передавай data_interval_start/end в manifest, объясни catchup/backfill на двух прошлых датах. Не запускай массовый backfill. Временно вызови исключение перед publish, повтори только упавший шаг, сравни release и число результатов; сохрани DAG run ID/task ID/attempt/run_key/artifact в report.md.

## Среда и зависимости

Базовая среда из SETUP: Python, pytest; CPU, Linux/macOS.

Зависит от 05-airflow/02-gate-retry. Offline доказывает преобразование интервала и переход состояния; scheduler retry/catchup проверяй в Airflow отдельно. Ручная приёмка требует логов конкретной task, а не только зелёного DAG.

## Запуск и результат

Из корня репозитория:

```bash
make task TASK=05-airflow/03-failure-intervals
```

До реализации ожидается RED: `NotImplementedError`, а не ошибка импорта зависимостей. После реализации все offline-тесты должны быть зелёными. Они создают временные данные через pytest tmp_path; полный housing автоматически не скачивается.

Это задание использует функции; импортируй заготовку через `course_tasks.load_task("05-airflow/03-failure-intervals")` из Python. CLI не требуется.

## Требования практического опыта

Временно вызови исключение перед publish, повтори только упавший шаг и проверь отсутствие дубликата. Затем добавь ежедневное расписание, передавай интервал в манифест и объясни catchup/backfill на примере двух прошлых дат. Не запускай массовый backfill на ноутбуке.

## Приёмка и очистка

Пройди все тесты `test_task.py`, сохрани перечисленные артефакты и добавь объяснение решений/ограничений в `report.md`. Для инфраструктурных опытов приложи реальные команды и вывод: offline проверки не доказывают развёртывание, доступность удалённого сервера или качество объяснения. Ручная оценка: воспроизводимость шагов, соответствие исходному контракту, объяснение причины сбоя и корректное восстановление.

После опыта останови стенд: `docker compose -f labs/airflow/compose.yaml down`. Uvicorn останови Ctrl+C. Не удаляй volume без экспорта истории; артефакты `work/` сохрани для следующих модулей.

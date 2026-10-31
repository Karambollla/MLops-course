# Практика: ClearML: задачи, артефакты и агенты

[Теория](README.md) · [Подсказки](hints.md)

## Основной путь: Mac CPU

Создай отдельное окружение по [SETUP](../../SETUP.md), установи `labs/clearml/requirements.txt` и housing с `--no-deps`.

```bash
CLEARML_OFFLINE_MODE=1 python labs/clearml/task.py
```

Заготовка создаёт offline Task, но учебный шаг ожидаемо падает до реализации. Подключи свой train CLI, залогируй параметры, data hash и реальные validation metrics; сохрани путь к offline session из вывода SDK. Успешный локальный train не называй remote execution.

## Дополнительный путь: Server и Agent

Только на совместимом Linux x86_64 с достаточной RAM:

```bash
docker compose -f labs/clearml/compose.yaml up -d
```

Проверь UI на 8088, API на 8008, file server на 8081. Выполни `clearml-init` в SDK-окружении, сохраняя credentials вне репозитория. Укажи собственные адреса: web host `http://127.0.0.1:8088`, API host `http://127.0.0.1:8008`, files host `http://127.0.0.1:8081`.

После реализации локального задания зарегистрируй **новый online-запуск**:

```bash
CLEARML_OFFLINE_MODE=0 python labs/clearml/task.py
```

Убедись, что Task появилась в UI вместе с реальными метриками и артефактами. Старая offline-сессия автоматически туда не переносится; альтернативой повторному запуску является импорт по руководству из теории. Для этого задания используем новый online-run.

Перед стартом агента убери offline-переменную из его терминала: `unset CLEARML_OFFLINE_MODE`. Starter дополнительно отключает offline для исполнения через Agent с помощью `Task.running_locally()`. Не удаляй эту проверку при реализации обучения. Для агента создай отдельный `.venv-clearml-agent` через Python 3.12 и установи только `clearml-agent==1.9.3`: не добавляй туда requirements обучения. У агента и задачи разные окружения, в том числе ограничения six. Запусти agent командой `clearml-agent daemon --queue default --foreground`. Клонируй собственную задачу в UI, отправь её в default и проверь, что agent исполняет конкретный код и параметры. Предоставь доступный agent путь к данным или свой versioned download step.

## Сравнение и отказ

Сравни один эксперимент в MLflow и ClearML: параметры, metrics, artifacts, lineage и способ повторного запуска. На серверном пути останови agent после получения задачи, зафиксируй состояние и восстановление. На offline-пути вместо этого проверь сохранение сессии при исключении и явно отметь, что очередь не проверена.

## Критерии готовности

- [ ] Реальный запуск связан с параметрами, данными и метриками.
- [ ] Объяснены SDK, Server, Agent и Queue.
- [ ] В отчёте указан реально пройденный уровень: offline либо server/agent.
- [ ] Сравнение с MLflow/Airflow содержит минимум два аргумента о сопровождении.

## Завершение

Agent останови Ctrl+C. Server: `docker compose -f labs/clearml/compose.yaml down`. Сначала экспортируй отчёт, затем при необходимости `down -v`. Offline-сессии остаются в cache ClearML; путь показывает SDK.

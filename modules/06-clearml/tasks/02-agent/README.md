# ClearML: Server и Agent

Зависит от 06-clearml/01-offline. Дополнительный путь только на совместимом Linux x86_64; queue не является worker.

## Что редактировать

Основная заготовка — `report.json`: заполни её собственными наблюдениями по `report.template.json`. В `solution.py` есть необязательный сборщик `collect_report()`, который можно реализовать для автоматизации read-only запросов; ручное заполнение отчёта тоже допустимо.

Готовый `grading.py` проверяет согласованность отчёта; писать свой валидатор не требуется. `scenario.json` содержит синтетический пример для тестов и не подтверждает выполнение практики. Сдавай свои измерения и команды, сохраняя ожидаемое поведение тестов.

## Подготовка и выполнение

Команды запускаются из корня репозитория. Общая установка — [SETUP](../../../../SETUP.md). Окружение CPU с pytest; SDK/CLI устанавливаются отдельно по SETUP и не нужны для сбора тестов. Не смешивай окружения agent и обучения (разные ограничения six). ARM server не объявлен проверенным.

Подними `docker compose -f labs/clearml/compose.yaml up -d`. Проверь web 8088, API 8008, files 8081; выполни clearml-init, credentials вне Git. Создай новый online-run `CLEARML_OFFLINE_MODE=0 python modules/06-clearml/tasks/01-offline/solution.py`. В отдельной Python 3.12 `.venv-clearml-agent` установи только `clearml-agent==1.9.3`; `unset CLEARML_OFFLINE_MODE`, затем `clearml-agent daemon --queue default --foreground`. Клонируй свой Task, отправь в default, предоставь agent версионированные данные. Сохрани реальные идентификаторы, окружение и параметры; проверь metrics/artifacts в UI.

Проверка выбранного задания:

```bash
make task TASK=06-clearml/02-agent
python scripts/run_task.py run 06-clearml/02-agent -- --report modules/06-clearml/tasks/02-agent/report.json
```

CLI читает JSON --report и печатает наблюдения. Содержательную схему проверяет pytest через готовый grading.py; --collect включает TODO автоматизации сбора.

## Контракт и проверка

`validate_report(report) -> {"remote_execution": True, "task_id": str}`. Требуются online, новый task_id != clone_of, очередь default, непустой agent_id, последовательность queued/in_progress/completed, 40 hex commit, версионированный data_source, доступный agent (URL или путь Linux; путь /Users ноутбука не подходит), 64 hex data hash, конечная MAE >= 0, model.joblib и три HTTP 200.

Схема JSON задаётся `report.template.json`; null нужно заменить измерениями. Возвращаемые значения и отрицательные примеры зафиксированы в `test_task.py`. Отсутствующие поля, несовместимые типы и противоречивые наблюдения должны приводить к `ValueError`. До реализации тесты **RED**: незаполненный report.json вызывает ValueError; предметная заготовка выбрасывает `NotImplementedError`; это ожидаемый незавершённый код, а не успешный тест.

Офлайн-проверки проверяют числа, переходы состояний и согласованность наблюдений. Они не доказывают реальный запуск стенда. Вручную предъяви команды, время, обезличенные ответы и объяснение причин; совпадение схемы без реальных наблюдений не закрывает практику. Тесты не разворачивают и не удаляют ресурсы. Любые добавленные live-проверки разрешены только с `MLOPS_RUN_INTEGRATION=1`, читают уже работающий стенд и не меняют его.

## Завершение

Agent: Ctrl+C. `docker compose -f labs/clearml/compose.yaml down`; down -v только после экспорта собственных данных.

Зависимости и теория: [модуль](../../README.md), [подсказки](../../hints.md). Не сохраняй credentials, токены или чувствительные state/plan в Git.

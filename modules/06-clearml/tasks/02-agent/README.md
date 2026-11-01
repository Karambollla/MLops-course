# ClearML: Server и Agent (Linux x86_64)

Практика после 01-offline; нужен совместимый Linux x86_64, Docker Compose,
SDK из labs/clearml/requirements.txt и отдельное Python 3.12 окружение agent.
На ARM используй offline путь; серверный стенд на ARM не объявлен проверенным.
Это руководство по реальному исполнению, автоматического теста удалённой очереди нет.

```bash
docker compose -f labs/clearml/compose.yaml up -d
curl --fail --max-time 10 http://localhost:8088/
clearml-init
CLEARML_OFFLINE_MODE=0 python modules/06-clearml/tasks/01-offline/solution.py --data work/housing.csv --output modules/06-clearml/tasks/02-agent/output --seed 42
```

`clearml-init` настраивает API localhost:8008, web localhost:8088, files localhost:8081;
credentials остаются в пользовательской конфигурации вне Git.
Иллюстрация: curl завершился с exit 0, SDK показывает новый Task ID и online UI.

В отдельном окружении установи `clearml-agent==1.9.3`, затем:

```bash
unset CLEARML_OFFLINE_MODE
clearml-agent daemon --queue default --foreground
```

В UI клонируй свой online Task и отправь клон в default. Настрой его CLI --data и
--output на пути, доступные Linux agent; `/Users/...` ноутбука ему недоступен.
Используй версионированный CSV, Git commit и зависимости проекта, проверь seed/hash.
Иллюстрация правильного результата в UI: новый ID отличается от исходного,
очередь default, реальный worker в Execution, статус queued → in_progress → completed;
MAE/RMSE и model.joblib/manifest.json соответствуют обучению на agent.
Пустая очередь или ручной локальный запуск сами по себе этот результат не дают.

Останови agent Ctrl+C; после использования `docker compose -f labs/clearml/compose.yaml down`.
Сначала сохрани нужные задачи и артефакты; удаление volumes необязательно.

Все команды — из корня репозитория после [SETUP](../../../../SETUP.md).
Выводы ниже иллюстрируют инварианты; это не запись успешного выполнения.
Отчёт, JSON-подтверждение и письменное описание не требуются.
[Теория](../../README.md) · [Подсказки](../../hints.md)

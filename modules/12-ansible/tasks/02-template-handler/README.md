# Доставить конфигурацию и обработать её изменение

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

В первом задании содержимое env-файла было постоянным. Теперь число процессов передаётся параметром. Нужно проверить значение, получить новый файл и выполнить связанное действие только при реальном изменении. Эту связь обеспечивают template, `notify` и handler, разобранные в [главе](../../README.md#путь-от-переменной-до-файла-и-handler).

Редактируй [playbook.yaml](playbook.yaml) и при необходимости [housing.env.j2](housing.env.j2). В play уже есть `workers: 1`, но `tasks` и `handlers` пусты. Шаблон уже содержит `MODEL_PATH=/models/model.joblib` и `WORKERS={{ workers }}`. Compose/inventory подготовлены. Python-функции здесь не пишутся.

В контейнере нет systemd и работающего daemon. Вместо reload handler сохраняет SHA-256 текущего env-файла. Этот диагностический marker позволяет проверить, что обработано именно новое содержимое. Он не является перезапуском API.

## Шаг 1. Проверить вход и получить файл

`workers` задаёт число процессов в учебной конфигурации. При `-e workers=2` CLI может передать строку `"2"`. Принимай положительное целое и его корректное строковое представление. Ноль, отрицательное или дробное значение нельзя превращать в рабочее округлением или значением по умолчанию.

В `tasks` добавь `assert` до записи, создание каталога и `ansible.builtin.template`. Для путей используй следующее соответствие:

| Что | Путь и сторона | Что уже подготовлено |
|---|---|---|
| Исходник template | `/lab/housing.env.j2` на controller | Compose монтирует соседний шаблон read-only |
| Каталог назначения | `/course-output/config` на managed node | Его должна создать задача `file` |
| Полученный env | `/course-output/config/housing.env` | Template пишет MODEL_PATH и выбранный WORKERS |
| Результат на компьютере | `work/ansible-template/config/housing.env` | `/course-output` — bind mount этого каталога |

`src` читает controller, `dest` относится к managed node. В лабораторной они в одном контейнере, но роли путей различаются. Режимы задавай строками, например `'0755'` для каталога и `'0644'` для env. Если шаблон не найден, проверь mount и src прежде, чем менять Jinja2.

## Шаг 2. Связать изменение с handler

Добавь template-задаче `notify`, а в `handlers` — обработчик с точно совпадающим именем. После изменения template handler должен вычислить SHA-256 **фактических байтов** `/course-output/config/housing.env` и записать его в `/course-output/config/housing.env.sha256`.

Marker содержит только hex-сумму, без имени файла после пробела. Переводы строк входят в хеш. Не хешируй имя пути или строковое представление переменных. При повторе с тем же workers template не меняется, уведомления нет, handler не выполняется.

## Шаг 3. Выполнить переходы 1 → 2 → 2

Подготовь controller по [инструкции модуля](../../README.md#подготовка-к-заданиям). Сначала посмотри предварительный diff, затем примени конфигурацию:

```bash
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml --check --diff -e workers=1
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=1
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=2
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=2
```

`-i inventory.ini` выбирает группу `lab` в контейнере, `-e` переопределяет workers. `--check --diff` показывает предполагаемую запись. На чистом каталоге зависимым задачам может не хватать ещё не созданного файла. Ограничения разобраны [в главе](../../README.md#check-mode-ошибки-и-секреты). Check не заменяет apply.

При первом apply создаются env и marker. Если файлы уже совпадали с workers=1, изменений может не быть. Переход 1→2 должен изменить template и вызвать handler. Повтор 2→2 должен дать `changed=0` без выполнения handler. Наблюдай имена задач, handler output и recap, а также фактические файлы.

Отдельно проверь недопустимый вход:

```bash
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=0
```

Ожидается ошибка `assert` до записи. Env и marker после этого должны сохранить предыдущее содержимое с `WORKERS=2`.

## Проверка результата и завершение

```bash
MLOPS_RUN_INTEGRATION=1 make task TASK=12-ansible/02-template-handler
```

Тест только читает файлы `work/ansible-template/config`: требует `MODEL_PATH=/models/model.joblib`, `WORKERS=2` и marker, совпадающий с SHA-256 env. Он не запускает Ansible и не доказывает историю уведомлений: её ты наблюдаешь в предыдущем шаге. Без флага тест пропущен.

`run --rm` удаляет controller, сохраняя файлы в bind mount. Останови task-local конфигурацию:

```bash
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml down
```

Шаблон и playbook остаются исходниками настройки, а `work/ansible-template` — результатом применения.

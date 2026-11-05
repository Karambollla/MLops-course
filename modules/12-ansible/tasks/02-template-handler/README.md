# Template и handler

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем связывать изменение с действием

Доставка нового env-файла и применение его содержимого сервисом — разные этапы. Handler связывает их: запускается при изменении, а повтор с теми же параметрами не создаёт лишнего действия. В этом стенде вместо daemon используется проверяемый digest файла.

Даны task-local Compose/inventory и шаблон с `MODEL_PATH` и `WORKERS`. Playbook оставлен с пустыми tasks/handlers. Результаты сохраняются в отдельном `work/ansible-template`. Ты реализуешь валидацию, рендер и реакцию на изменение. Сначала прочти [путь переменной до handler](../../README.md#путь-от-переменной-до-файла-и-handler) и [ограничения check mode](../../README.md#check-mode-ошибки-и-секреты).

## Редактируемые файлы и аргументы Ansible

| Файл или параметр | Тип и формат | Происхождение и роль | Пример |
|---|---|---|---|
| `playbook.yaml` | YAML play с `vars`, `tasks`, `handlers` | Учебная заготовка. Добавь assert до записи, каталог, template, notify и handler | `workers` исходно `1` |
| `housing.env.j2` | Текстовый Jinja2-шаблон на controller | Исходник template. Сохраняй MODEL_PATH и подставляй workers | `WORKERS={{ workers }}` |
| `workers`, CLI `-e workers=2` | Положительное целое либо его строковое представление из CLI | Переменная управляет содержимым env. Не округляй дроби и не заменяй 0 на 1 | `1`, `"2"` |
| `-i inventory.ini` | Путь внутри `/lab` controller | Готовый inventory выбирает localhost группы lab через local connection | Не SSH-хост компьютера |
| Template `src`, `dest` | Пути на controller и managed node | `src` читает `housing.env.j2`, `dest` пишет env в persistent mount | `/course-output/config/housing.env` |
| Marker handler | Файл с одной SHA-256 hex-суммой текущего env | Пишется после изменения template и проверяется по фактическим байтам | `/course-output/config/housing.env.sha256` |
| `--check --diff` | Флаги предварительного просмотра | Оценивают изменение и показывают diff, не заменяют apply | На чистом каталоге возможны ограничения зависимых tasks |

Compose уже монтирует шаблон в `/lab/housing.env.j2` и `work/ansible-template` в `/course-output`. Если src не найден, сначала проверь mount и путь, а не выражение Jinja2. Создай каталог `config` до template. Режимы файлов задавай строками, например `'0644'`, каталога — `'0755'`.

Python-функции в этой теме не пишутся. Live-тест читает `work/ansible-template/config/housing.env`, требует `MODEL_PATH=/models/model.joblib`, `WORKERS=2` и сверяет соседний marker с SHA-256 реальных байтов. Успех не доказывает, когда именно запускался handler: эту часть наблюдай в выводе Ansible.

## Технический контракт

Корректное положительное целое workers даёт `WORKERS=<значение>` в `/course-output/config/housing.env`. MODEL_PATH сохраняется. При workers=0 assert должен остановить play до записи. Переход 1→2 уведомляет handler, который сохраняет SHA256 фактических байтов env в соседнем `.sha256`. Повтор 2→2 даёт changed=0. Например, digest с именем файла после пробела не удовлетворяет контракту: marker содержит только hex-сумму. `-e workers=2` может передавать строковое значение — проверь формат и числовой смысл, не полагайся на Python-тип без учёта CLI. Тест читает конечные файлы, историю notify наблюдаешь в Ansible output.

## Реализация и запуск

Редактируй playbook.yaml и housing.env.j2. Добавь assert: workers — положительное целое, template в /course-output/config/housing.env, notify и handler. В этом контейнере нет systemd: handler должен записать SHA256 **байтов текущей конфигурации** в /course-output/config/housing.env.sha256. Это диагностический marker, а не restart daemon. Compose уже монтирует template.

```bash
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml --check --diff -e workers=1
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=1
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=2
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=2
MLOPS_RUN_INTEGRATION=1 make task TASK=12-ansible/02-template-handler
```

Первый apply создаёт файл, переход 1→2 меняет template и вызывает handler, повтор workers=2 даёт changed=0 без handler. На чистом каталоге check mode может не уметь сравнить ещё не созданный файл. Запусти с workers=0: assert должен завершиться ошибкой до записи. Live-тест читает work/ansible-template/config и сравнивает конфигурацию и digest. Он не доказывает историю запусков и не запускает Ansible. Историю изменений наблюдай по recap и handler output. После практики останови task-local compose.

# Два применения одной настройки

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

Нужно доставить один env-файл и убедиться, что повтор не переписывает его без причины. Первый запуск показывает получение нужного состояния, второй — поведение при тех же входах. Ты выполнишь готовый playbook дважды и напишешь функции разбора сводки Ansible.

В [playbook.yaml](playbook.yaml) уже есть создание каталога и запись `housing.env` через `copy`. [inventory.ini](inventory.ini) выбирает локальный узел контейнера. [compose.yaml](compose.yaml) сохраняет результаты в `work/ansible`. Настоящий Housing API не запускается. Место выполнения объясняется в [главе](../../README.md#controller-inventory-play-и-module).

Редактируй только две заготовки в [solution.py](solution.py). TODO в готовом playbook относится к последующей теме: здесь template и handler добавлять не нужно, они реализуются в отдельном задании 02.

## Шаг 1. Разобрать сводку одного запуска

После списка задач Ansible печатает `PLAY RECAP` — результаты по каждому узлу. Например:

```text
PLAY RECAP ***
localhost : ok=2 changed=2 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

Здесь `localhost` — имя узла inventory, `changed=2` — две задачи изменили состояние. Смысл всех счётчиков, включая то, что `ok` включает изменившие состояние задачи, разобран в [главе о recap](../../README.md#что-означают-changed-и-play-recap).

```python
def parse_recap(text: str) -> dict[str, dict[str, int]]:
    ...
```

`text` — полный stdout одного запуска Ansible, строка. Функция извлекает только recap: task output до него не заменяет сводку. Верни словарь host → семь целочисленных счётчиков `ok`, `changed`, `unreachable`, `failed`, `skipped`, `rescued`, `ignored`. Для примера выше:

```python
{
    "localhost": {
        "ok": 2, "changed": 2, "unreachable": 0, "failed": 0,
        "skipped": 0, "rescued": 0, "ignored": 0,
    }
}
```

Обработай и несколько hosts, например `node-a`, `node_b`. Пустой текст или отсутствие recap дают `ValueError`. Сам parser не требует `changed=0`: первый успешный запуск вправе менять файлы.

## Шаг 2. Сравнить два запуска

```python
def compare_runs(first: str, second: str) -> dict:
    ...
```

`first` и `second` — исходные тексты двух запусков, ещё не словари. Разбери оба через `parse_recap` и проверь:

- Множества hosts совпадают. Порядок строк не важен.
- У каждого host в обоих запусках `failed=0` и `unreachable=0`.
- У каждого host во втором запуске `changed=0`.

При успехе верни карту host → changed второго запуска, например `{"localhost": 0}`. Любое нарушение даёт `ValueError`. Первый запуск тоже может иметь `changed=0`, если нужный файл уже существует. Функция проверяет текст, а происхождение и реальные побочные эффекты наблюдаются отдельно.

Проверь функции на фиксированных входах без Ansible и Docker:

```bash
make task TASK=12-ansible/01-idempotency
```

До реализации ожидается `NotImplementedError`. Тесты включают многоузловой вывод, ошибки любого host и CLI с путями, содержащими пробелы.

## Шаг 3. Получить настоящий вывод

Подготовь controller по [инструкции модуля](../../README.md#подготовка-к-заданиям). Каталог `work/ansible` должен существовать до перенаправления stdout. Сохрани два запуска с одинаковыми входами:

```bash
docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller > work/ansible/first.txt
docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller > work/ansible/second.txt
python modules/12-ansible/tasks/01-idempotency/solution.py work/ansible/first.txt work/ansible/second.txt
```

CLI принимает два обязательных пути, читает файлы как текст и печатает JSON результата `compare_runs`. Ожидается `{"localhost": 0}`. Посмотри оба сохранённых recap и файл `work/ansible/config/housing.env`: он содержит `MODEL_PATH=/models/model.joblib` и `WORKERS=1`. Повторный controller видит файл предыдущего запуска благодаря bind mount, хотя сам контейнер одноразовый.

Если второй запуск сообщает изменение, сначала сравни фактические файлы и права. Подмена вывода на `changed=0` не проверяет идемпотентность. `run --rm` удаляет завершившийся controller, а результаты остаются в `work/ansible`. Команда остановки — в [очистке модуля](../../README.md#остановка-и-очистка).

# Два запуска Ansible

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем смотреть два запуска

Первый успешный playbook создаёт конфигурацию, второй показывает, нужна ли повторная запись при тех же входах. Это полезно для автоматической настройки: случайный перезапуск или дописывание строки при каждом применении создавали бы ненужное изменение работающего узла.

Task-local playbook уже создаёт каталог и пишет учебный env-файл. Controller и managed node находятся внутри одного контейнера, файлы сохраняются в `work/ansible`. Ты реализуешь разбор результата в Python. Тесты не запускают Ansible. Место выполнения объясняется в [inventory и module](../../README.md#controller-inventory-play-и-module), смысл счётчиков — в [PLAY RECAP](../../README.md#что-означают-changed-и-play-recap).

## Входы функций

```python
def parse_recap(text: str) -> dict[str, dict[str, int]]:
    ...

def compare_runs(first: str, second: str) -> dict:
    ...
```

| Функция и аргумент | Тип и формат | Откуда берётся и зачем нужен | Пример |
|---|---|---|---|
| `parse_recap`: `text` | `str`, полный stdout Ansible с секцией PLAY RECAP | Фиксированный текст в тестах или содержимое сохранённого вывода ручного playbook | Строка PLAY RECAP и строка `localhost : ok=2 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0` |
| `compare_runs`: `first` | `str`, текст первого запуска, ещё не dict | Первый исходный вывод. Проверяется успешность всех hosts | Recap с `changed=2` |
| `compare_runs`: `second` | `str`, текст повторного запуска | Второй исходный вывод с теми же hosts. Изменений при повторе быть не должно | Recap тех же hosts с `changed=0` |

`parse_recap` извлекает host и семь целочисленных счётчиков: `ok`, `changed`, `unreachable`, `failed`, `skipped`, `rescued`, `ignored`. Текст задач до recap не является сводкой. Для одной строки выше результат имеет форму:

```python
{
    "localhost": {
        "ok": 2, "changed": 0, "unreachable": 0, "failed": 0,
        "skipped": 0, "rescued": 0, "ignored": 0,
    }
}
```

В многоузловом выводе будет отдельный ключ каждого host, например `node-a` и `node_b`. Parser не запускает Ansible и не требует, чтобы changed был нулевым. Отсутствие recap или пустой вывод дают `ValueError`.

`compare_runs` принимает два текста, вызывает разбор и сравнивает результаты. Требуются одинаковые множества hosts, `failed=unreachable=0` у каждого host в обоих запусках и `changed=0` во втором. Порядок строк hosts не важен. Первый запуск уже может иметь `changed=0`, если файлы существовали. При успехе верни `{"localhost": 0}` либо такую же карту для всех hosts. Нарушения дают `ValueError`. Смысл остальных счётчиков разобран в [PLAY RECAP](../../README.md#что-означают-changed-и-play-recap).

## Реализация и запуск

Реализуй две функции в `solution.py`. Подготовь controller по [инструкции модуля](../../README.md#подготовка-к-заданиям), затем выполни playbook дважды с одинаковыми входами:

```bash
docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller
docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller
make task TASK=12-ansible/01-idempotency
```

Первый создаёт work/ansible/config/housing.env. Второй показывает changed=0, failed=0, unreachable=0. Если файл уже существовал, первый тоже может быть no-op. Parser проверяется на фиксированном тексте. Тест не запускает playbook. Для собственного вывода CLI принимает пути двух сохранённых recap.

## Собственный вывод и CLI

Compose первого задания уже содержит рабочий playbook с созданием каталога и copy. Python-функции редактируй в `solution.py`. Учебный TODO в playbook не нужен для тестов parser: template и handler реализуются в отдельном задании 02.

Сохрани stdout двух реальных запусков, например в `work/ansible/first.txt` и `work/ansible/second.txt`. CLI принимает два пути из корня курса и читает их как текст:

```bash
python modules/12-ansible/tasks/01-idempotency/solution.py work/ansible/first.txt work/ansible/second.txt
```

Пути с пробелами заключай в кавычки. CLI возвращает JSON host→changed второго запуска. Проверки Python не подтверждают происхождение текста, поэтому отдельно наблюдай реальный файл `work/ansible/config/housing.env`. Остановка controller и сохранение bind mount описаны в [очистке модуля](../../README.md#остановка-и-очистка).

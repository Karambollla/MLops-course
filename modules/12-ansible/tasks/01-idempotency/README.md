# Два запуска Ansible

## Зачем смотреть два запуска

Первый успешный playbook создаёт конфигурацию, второй показывает, нужна ли повторная запись при тех же входах. Это полезно для автоматической настройки: случайный перезапуск или дописывание строки при каждом применении создавали бы ненужное изменение работающего узла.

Task-local playbook уже создаёт каталог и пишет учебный env-файл. Controller и managed node находятся внутри одного контейнера, файлы сохраняются в `work/ansible`. Ты реализуешь разбор результата в Python; тесты не запускают Ansible. Место выполнения объясняется в [inventory и module](../../README.md#controller-inventory-play-и-module), смысл счётчиков — в [PLAY RECAP](../../README.md#что-означают-changed-и-play-recap).

## Контракт функций

`parse_recap(text)` получает текст с PLAY RECAP и возвращает карту host→счётчики. `compare_runs(first, second)` сравнивает две такие записи. Например, `node: ok=2 changed=2 ... failed=0` и затем тот же host с `changed=0` дают `{"node": 0}` при нулевых failed/unreachable обоих запусков. Другой набор hosts или провал первого запуска нельзя принять за успешный повтор. Сохранённый реальный вывод можно передать существующему CLI двумя путями файлов; это технические данные для parser, не отдельное описание работы.

## Реализация и запуск

Реализуй `parse_recap(text)` и `compare_runs(first,second)` в solution.py. Parser возвращает host→dict с числовыми ok/changed/unreachable/failed/skipped/rescued/ignored. Пустой вывод/отсутствие recap — ValueError. compare_runs требует одинаковые hosts, failed=unreachable=0 в обоих запусках и changed=0 во втором; верни host→changed второго запуска.

```bash
docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller
docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller
make task TASK=12-ansible/01-idempotency
```

Первый создаёт work/ansible/config/housing.env; второй показывает changed=0, failed=0, unreachable=0. Если файл уже существовал, первый тоже может быть no-op. Parser проверяется на фиксированном тексте; тест не запускает playbook. Для собственного вывода CLI принимает пути двух сохранённых recap.

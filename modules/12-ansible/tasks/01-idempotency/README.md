# Ansible: два запуска

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## С чего начать

Открой `playbook.yaml` и `compose.yaml`: это локальные копии входа именно этого задания. Для разбора результата реализуй `parse_recap(text) -> dict[str, dict[str, int]]`: одна запись на host, значения ok/changed/unreachable/failed/skipped/rescued/ignored. Пустой вывод или отсутствие recap — ValueError. `compare_runs(first, second) -> dict` возвращает изменения по hosts второго запуска; запрещает failed/unreachable и ненулевой changed при повторе. Основная практика — два реальных применения playbook, а parser помогает проверить результат.

Запускай `docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller` дважды.

Подготовь [основное окружение](../../../../SETUP.md). Все команды ниже выполняются из корня курса. Платформа задания: **cpu**. Функции и ожидаемые результаты описаны также в `test_task.py`; тесты используют небольшие фиксированные данные.

## Исходное задание

```bash
docker compose -f labs/ansible/compose.yaml run --rm controller
docker compose -f labs/ansible/compose.yaml run --rm controller
```

Первый создаёт `work/ansible/config/housing.env`; второй должен показать changed=0. Конфигурация сохраняется на host, поэтому новые одноразовые controller-контейнеры видят предыдущий результат.

## Проверка

```bash
make task TASK=12-ansible/01-idempotency
```

Для Python CLI:

```bash
python scripts/run_task.py run 12-ansible/01-idempotency -- --help
```

До реализации функции ожидается `NotImplementedError`; для отчётов — ошибка незаполненного поля. Исправляй заготовку или собственный результат, сохраняя ожидаемое поведение тестов. Офлайн-тест не подтверждает действия на внешнем стенде: проверки, требующие работающего сервиса, включаются явно через `MLOPS_RUN_INTEGRATION=1`.

## Критерии и завершение

Покажи результаты исходного задания и объясни позитивные и негативные случаи из тестов. Сохрани собственные измерения и команды в work/. Затем останови стенд по общей инструкции practice.md модуля.

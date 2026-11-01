# Практика: Ansible: настройка и идемпотентность

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Ansible: два запуска](tasks/01-idempotency/README.md) | [Заготовка](tasks/01-idempotency/solution.py) · [тесты](tasks/01-idempotency/test_task.py) | cpu |
| [Ansible: template и handler](tasks/02-template-handler/README.md) | [Заготовка](tasks/02-template-handler/playbook.yaml) · [тесты](tasks/02-template-handler/test_task.py) | cpu |
| [Границы Dockerfile, Terraform и Ansible](tasks/03-tool-boundaries/README.md) | [Заготовка](tasks/03-tool-boundaries/comparison.md) · [тесты](tasks/03-tool-boundaries/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=12-ansible/01-idempotency
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

```bash
mkdir -p work/ansible
docker compose -f labs/ansible/compose.yaml build
docker compose -f labs/ansible/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml --syntax-check
```

## Завершение

`docker compose -f labs/ansible/compose.yaml down`. Отчёт и созданные файлы остаются в `work/ansible`; удали их только после фиксации результатов.

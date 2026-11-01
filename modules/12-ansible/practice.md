# Практика: Ansible: настройка и идемпотентность

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Ansible: два запуска](tasks/01-idempotency/README.md) | [Старт](tasks/01-idempotency/solution.py) · [Тесты функций](tasks/01-idempotency/test_task.py) | cpu |
| [Ansible: template и handler](tasks/02-template-handler/README.md) | [Старт](tasks/02-template-handler/playbook.yaml) · [Проверка стенда](tasks/02-template-handler/test_task.py) | cpu |
| [Границы Dockerfile, Terraform и Ansible](tasks/03-tool-boundaries/README.md) | Руководство с примерами | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=12-ansible/01-idempotency
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Функции проверяются прямо на фиксированных входах. Live-проверки читают существующий стенд только с MLOPS_RUN_INTEGRATION=1; guides не требуют отдельной сдачи.

## Подготовка

```bash
mkdir -p work/ansible
docker compose -f labs/ansible/compose.yaml build
docker compose -f labs/ansible/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml --syntax-check
```

## Завершение

`docker compose -f labs/ansible/compose.yaml down`. Созданные файлы остаются в `work/ansible`; удали их только после фиксации результатов.

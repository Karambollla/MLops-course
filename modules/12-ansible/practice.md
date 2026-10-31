# Практика: Ansible: настройка и идемпотентность

[Теория](README.md) · [Подсказки](hints.md)

## Подготовка

```bash
mkdir -p work/ansible
docker compose -f labs/ansible/compose.yaml build
docker compose -f labs/ansible/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml --syntax-check
```

## Задание 1. Два запуска

```bash
docker compose -f labs/ansible/compose.yaml run --rm controller
docker compose -f labs/ansible/compose.yaml run --rm controller
```

Первый создаёт `work/ansible/config/housing.env`; второй должен показать changed=0. Конфигурация сохраняется на host, поэтому новые одноразовые controller-контейнеры видят предыдущий результат.

## Задание 2. Параметры и handler

Добавь template с переменной WORKERS, ограниченной положительным целым. Измени WORKERS с 1 на 2, покажи один ожидаемый change и срабатывание handler только при изменении. Для контейнера без systemd используй marker с понятным назначением. После повторного запуска снова changed=0.

Смонтируй свой template в controller через дополнительный volume Compose: текущий стенд монтирует только inventory/playbook. Проверь `--check --diff` перед применением и сравни с реальностью.

## Задание 3. Объяснение границ

Составь таблицу Dockerfile/Terraform/Ansible: что описывает каждый, где хранится состояние, как повторить и откатить изменение. Дополнительное задание — отдельный SSH-enabled managed container; он не нужен для интенсива.

## Критерии готовности

- [ ] Второй запуск даёт changed=0.
- [ ] Изменение переменной меняет только ожидаемую конфигурацию.
- [ ] Handler не выполняется без изменения файла.
- [ ] macOS и чужие узлы не затронуты.

## Завершение

`docker compose -f labs/ansible/compose.yaml down`. Отчёт и созданные файлы остаются в `work/ansible`; удали их только после фиксации результатов.

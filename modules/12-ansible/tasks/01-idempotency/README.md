# Два запуска Ansible

Реализуй `parse_recap(text)` и `compare_runs(first,second)` в solution.py. Parser возвращает host→dict с числовыми ok/changed/unreachable/failed/skipped/rescued/ignored. Пустой вывод/отсутствие recap — ValueError. compare_runs требует одинаковые hosts, failed=unreachable=0 в обоих запусках и changed=0 во втором; верни host→changed второго запуска.

```bash
docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller
docker compose -f modules/12-ansible/tasks/01-idempotency/compose.yaml run --rm controller
make task TASK=12-ansible/01-idempotency
```

Первый создаёт work/ansible/config/housing.env; второй показывает changed=0, failed=0, unreachable=0. Если файл уже существовал, первый тоже может быть no-op. Parser проверяется на фиксированном тексте; тест не запускает playbook. Для собственного вывода CLI принимает пути двух сохранённых recap. Проза для сдачи не нужна.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

# Template и handler

Редактируй playbook.yaml и housing.env.j2. Добавь assert: workers — положительное целое, template в /course-output/config/housing.env, notify и handler. В этом контейнере нет systemd: handler должен записать SHA256 **байтов текущей конфигурации** в /course-output/config/housing.env.sha256. Это диагностический marker, а не restart daemon. Compose уже монтирует template.

```bash
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml --check --diff -e workers=1
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=1
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=2
docker compose -f modules/12-ansible/tasks/02-template-handler/compose.yaml run --rm controller ansible-playbook -i inventory.ini playbook.yaml -e workers=2
MLOPS_RUN_INTEGRATION=1 make task TASK=12-ansible/02-template-handler
```

Первый apply создаёт файл, переход 1→2 меняет template и вызывает handler, повтор workers=2 даёт changed=0 без handler. На чистом каталоге check mode может не уметь сравнить ещё не созданный файл. Запусти с workers=0: assert должен завершиться ошибкой до записи. Live-тест читает work/ansible-template/config и сравнивает конфигурацию и digest; он не доказывает историю запусков и не запускает Ansible. Историю изменений наблюдай по recap и handler output, отдельный отчёт не нужен. После практики останови task-local compose.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

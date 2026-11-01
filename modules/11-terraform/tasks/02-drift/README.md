# Обнаружение drift

Все три задачи используют **один** каталог `modules/11-terraform/tasks/01-repeat` и его существующий state. Не применяй labs/terraform параллельно с тем же именем контейнера. Terraform 1.11.4/provider 3.0.2 закреплены в main.tf. Docker endpoint узнай через `docker context inspect --format '{{.Endpoints.docker.Host}}'` и задай `TF_VAR_docker_host`.

После задания 01 вручную удали только учебный контейнер:

```bash
docker rm -f mlops-course-terraform
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -detailed-exitcode
```

Ожидается create для docker_container.web и код 2, означающий найденное изменение. Запусти live-тест **до восстановления**. Конфигурацию и state не редактируй ради имитации drift. Затем вручную просмотри plan и выполни apply; HTTP снова 200, следующий plan без изменений. Тест читает настоящий plan и не восстанавливает контейнер.

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/02-drift
```

Рабочий каталог задаётся явно; нет CLI/provider/state — тест падает с подсказкой. Проверки не выполняют init/apply/destroy и не выводят plan/state. Завершив все три задачи, вручную выполни `terraform -chdir=modules/11-terraform/tasks/01-repeat destroy`, затем удали saved plan; state и plan не коммить.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

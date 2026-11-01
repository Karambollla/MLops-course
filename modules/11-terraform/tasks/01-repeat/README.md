# Повторяемая инфраструктура

Все три задачи используют **один** каталог `modules/11-terraform/tasks/01-repeat` и его существующий state. Не применяй labs/terraform параллельно с тем же именем контейнера. Terraform 1.11.4/provider 3.0.2 закреплены в main.tf. Docker endpoint узнай через `docker context inspect --format '{{.Endpoints.docker.Host}}'` и задай `TF_VAR_docker_host`.

Изучи и при необходимости измени main.tf. Подготовка выполняется вручную:

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat init
terraform -chdir=modules/11-terraform/tasks/01-repeat validate
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -out=course.tfplan
terraform -chdir=modules/11-terraform/tasks/01-repeat apply course.tfplan
curl -I http://127.0.0.1:8099
```

Ожидается HTTP200. Повторный plan должен показать No changes. Измени внешний порт 8099→8100 и изучи plan: docker_container.web заменяется; применяй только после просмотра. Верни желаемую конфигурацию и её состояние перед no-op тестом. Тест не применяет plan.

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/01-repeat
```

Рабочий каталог задаётся явно; нет CLI/provider/state — тест падает с подсказкой. Проверки не выполняют init/apply/destroy и не выводят plan/state. Завершив все три задачи, вручную выполни `terraform -chdir=modules/11-terraform/tasks/01-repeat destroy`, затем удали saved plan; state и plan не коммить.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

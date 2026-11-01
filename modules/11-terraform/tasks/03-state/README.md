# State и реальные привязки

Все три задачи используют **один** каталог `modules/11-terraform/tasks/01-repeat` и его существующий state. Не применяй labs/terraform параллельно с тем же именем контейнера. Terraform 1.11.4/provider 3.0.2 закреплены в main.tf. Docker endpoint узнай через `docker context inspect --format '{{.Endpoints.docker.Host}}'` и задай `TF_VAR_docker_host`.

На восстановленном стенде:

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat state list
docker inspect --format '{{.Id}}' mlops-course-terraform
```

Ожидаются docker_image.web и docker_container.web; тест сравнивает фактический ID Docker с ID в terraform show -json, не печатая state. Docker CLI должен использовать тот же endpoint, что Terraform.

Разбор без удаления state: HCL описывает желаемое состояние, state связывает address с ID, .terraform.lock.hcl закрепляет версии/checksums provider. При потере state ресурс существует, но Terraform может предложить create и столкнуться с занятым именем. `terraform import docker_container.web <actual-ID>` восстанавливает привязку в соответствующем каталоге; не выполняй import в уже связанном состоянии. Командная работа требует remote backend с locking и ограничением доступа. sensitive скрывает вывод, но не шифрует state. Отдельное design.md не требуется.

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/03-state
```

Рабочий каталог задаётся явно; нет CLI/provider/state — тест падает с подсказкой. Проверки не выполняют init/apply/destroy и не выводят plan/state. Завершив все три задачи, вручную выполни `terraform -chdir=modules/11-terraform/tasks/01-repeat destroy`, затем удали saved plan; state и plan не коммить.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

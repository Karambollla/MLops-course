# State и реальные привязки

## Зачем сравнивать ID, а не имя

HTTP200 по ожидаемому адресу не доказывает, что отвечает именно объект, которым управляет текущая конфигурация. State связывает локальный адрес ресурса с реальным ID; эта связь позволяет Terraform планировать дальнейшие изменения без угадывания по имени.

Нужен восстановленный контейнер после задания 02 и тот же рабочий каталог. Ты читаешь существующие связи; удалять state для опыта не требуется. Разобраны [назначение state](../../README.md#конфигурация-и-реальные-привязки) и [его хранение в команде](../../README.md#state-lock-файл-и-работа-команды).

## Технический контракт

В state присутствуют `docker_image.web` и `docker_container.web`. ID контейнера из `terraform show -json` равен `.Id`, полученному Docker CLI из того же daemon. Например, Terraform address `docker_container.web` может быть связан с длинным ID `ab12…`; имя `web` не обязано встречаться в имени контейнера. Lock-файл provider не заменяет эту связь. Тест сравнивает значения без публикации state; JSON-вывод нельзя бездумно сохранять в общий лог, потому что в других проектах он содержит секреты.

## Проверка привязок

Все три задачи используют **один** каталог `modules/11-terraform/tasks/01-repeat` и его существующий state. Не применяй labs/terraform параллельно с тем же именем контейнера. Terraform 1.11.4/provider 3.0.2 закреплены в main.tf. Docker endpoint узнай через `docker context inspect --format '{{.Endpoints.docker.Host}}'` и задай `TF_VAR_docker_host`.

На восстановленном стенде:

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat state list
docker inspect --format '{{.Id}}' mlops-course-terraform
```

Ожидаются docker_image.web и docker_container.web; тест сравнивает фактический ID Docker с ID в terraform show -json, не печатая state. Docker CLI должен использовать тот же endpoint, что Terraform.

Разбор без удаления state: HCL описывает желаемое состояние, state связывает address с ID, .terraform.lock.hcl закрепляет версии/checksums provider. При потере state ресурс существует, но Terraform может предложить create и столкнуться с занятым именем. `terraform import docker_container.web <actual-ID>` восстанавливает привязку в соответствующем каталоге; не выполняй import в уже связанном состоянии. Командная работа требует remote backend с locking и ограничением доступа. sensitive скрывает вывод, но не шифрует state.

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/03-state
```

Рабочий каталог задаётся явно; нет CLI/provider/state — тест падает с подсказкой. Проверки не выполняют init/apply/destroy и не выводят plan/state. Завершив все три задачи, вручную выполни `terraform -chdir=modules/11-terraform/tasks/01-repeat destroy`, затем удали saved plan; state и plan не коммить.

# Найти удаление вне Terraform и восстановить ресурс

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

После первого задания конфигурация требует web-контейнер, state знает его ID, Docker действительно его запускает. Теперь удали объект напрямую через Docker. Конфигурация не менялась, но окружение ей больше не соответствует. Такое расхождение называют **drift**.

Новый `main.tf` в папке 02 не нужен. Продолжай работать с `modules/11-terraform/tasks/01-repeat`, прежним state и Docker endpoint из [подготовки](../../README.md#подготовка-к-заданиям). Ты меняешь реальный объект и наблюдаешь план восстановления. Механику чтения трёх источников объясняет [глава](../../README.md#повтор-замена-и-drift).

## Шаг 1. Создать расхождение

Убедись, что повторный plan задания 01 был без изменений. Удали только учебный контейнер, не image, HCL или state:

```bash
docker rm -f mlops-course-terraform
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -detailed-exitcode
```

Ожидается создание `docker_container.web`, код 2. Provider обращается к Docker и не находит прежний ID, хотя HCL продолжает требовать этот объект. Код 2 здесь сообщает о необходимых действиях. Terraform не следит за ресурсом непрерывно: до нового apply контейнер останется отсутствующим.

Если plan не замечает удаление, проверь совпадение Docker context и `TF_VAR_docker_host`. Не используй `-refresh=false`: этот флаг исключит нужное чтение актуального объекта. Удаление state моделировало бы потерю учёта, а не внешнее изменение инфраструктуры.

## Шаг 2. Проверить план до восстановления

Именно пока контейнер отсутствует, запусти:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/02-drift
```

Тест берёт уже существующий каталог и state. Он выполняет настоящий plan с `-detailed-exitcode`, сохраняет его во временный файл, читает `terraform show -json` и требует `resource_changes[].change.actions == ["create"]` для `docker_container.web` и код 2. Он не выполняет apply и не восстанавливает контейнер. Включённый тест требует готовых Terraform/provider/Docker. Без `MLOPS_RUN_INTEGRATION=1` он пропущен.

У теста отключена блокировка plan, поэтому не запускай одновременно apply или другой опыт с этим state. `MLOPS_TERRAFORM_DIR` и `TF_VAR_docker_host` остаются такими же, как в задании 01.

## Шаг 3. Восстановить реальный объект

После проверки создай и просмотри новый saved plan:

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -out=course.tfplan
terraform -chdir=modules/11-terraform/tasks/01-repeat apply course.tfplan
curl -I http://127.0.0.1:8099
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -detailed-exitcode
```

Ожидаются HTTP 200 и повтор без изменений с кодом 0. Восстановленный контейнер получает новый ID. State после apply связывает его с прежним адресом `docker_container.web`. Факт этой связи проверяется в [задании 03](../03-state/README.md).

Оставь ресурс для последней проверки. После неё используй [очистку модуля](../../README.md#остановка-и-очистка). Изменять state вручную или восстанавливать его из старой копии в этом опыте не требуется.

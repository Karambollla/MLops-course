# Проверить, каким объектом управляет Terraform

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

После восстановления HTTP снова отвечает, но по одному URL нельзя установить, какой объект обслуживает порт. Нужно проверить связь между объявлением Terraform и конкретным контейнером Docker. Для этого сравним ID из state с фактическим ID Docker.

Вход — восстановленный контейнер после [задания 02](../02-drift/README.md), существующий `modules/11-terraform/tasks/01-repeat/terraform.tfstate` и тот же Docker endpoint. Новые файлы или функции не создаются. HCL и state не редактируются. Назначение state разобрано в [главе о привязках](../../README.md#конфигурация-и-реальные-привязки).

## Прочитать и сопоставить связь

Из корня курса:

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat state list
docker inspect --format '{{.Id}}' mlops-course-terraform
```

В первом выводе ожидаются `docker_image.web` и `docker_container.web`. Это адреса объявлений Terraform. Во втором — ID реального Docker-контейнера. Локальное имя `web` не обязано присутствовать в Docker-имени.

Для программного чтения state Terraform предоставляет `terraform show -json`. Нужный фрагмент имеет такую форму:

```json
{
  "address": "docker_container.web",
  "values": {"id": "actual-docker-container-id"}
}
```

Он находится внутри `values.root_module.resources[]`. Строка `actual-docker-container-id` в примере обозначает настоящий ID, а не значение для копирования. JSON-вывод state в других проектах может содержать секреты, поэтому тест сравнивает значения внутри процесса и не печатает весь документ.

## Проверка

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/03-state
```

Тест читает `terraform show -json`, требует оба адреса и сравнивает `values.id` контейнера с `.Id` из `docker inspect`. Docker CLI должен обращаться к тому же daemon, что provider через `TF_VAR_docker_host`. При несовпадении сначала проверь context и каталог state. Тест не выполняет init/apply/destroy. Без флага он пропускается.

Lock-файл `.terraform.lock.hcl` не содержит эту связь: он закрепляет provider и checksums. Потеря state не уничтожает Docker-объект, но лишает Terraform прежней привязки. Для уже существующего объекта возможен import. В рабочем связанном состоянии выполнять его не нужно. Хранение state, locking и ограничения `sensitive` разобраны [в главе](../../README.md#state-lock-файл-и-работа-команды), без отдельного опыта удаления state.

## Завершение

Когда сравнение ID выполнено, ресурс больше не нужен. Из той же конфигурации и с тем же endpoint выполни:

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat destroy
```

Просмотри удаляемые ресурсы до подтверждения. Проверь отсутствие `mlops-course-terraform` в Docker. Из-за `keep_locally=true` скачанный image может остаться локально. Удали ненужный `course.tfplan`. State и планы в Git не добавляй. Не удаляй state до destroy: он нужен для обращения к управляемым объектам.

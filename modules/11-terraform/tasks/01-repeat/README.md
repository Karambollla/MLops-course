# Повторяемая инфраструктура

## Зачем нужен повторный plan

Успешное создание контейнера показывает только первый переход. Для повторяемой инфраструктуры важно, чтобы повторный запуск с теми же входами не пересоздавал исправный объект. Изменение порта затем показывает, какие свойства provider умеет менять на месте, а какие требуют замены.

В каталоге задания уже есть `main.tf` с Docker provider и loopback-портом. Требуется рабочий Docker daemon; housing bundle, kind и Vault не используются. Ты изучаешь или меняешь конфигурацию и вручную выполняешь просмотренные действия. Прочти [схему ресурсов](../../README.md#конфигурация-и-реальные-привязки) и [путь plan/apply](../../README.md#путь-init--plan--apply).

## Технический контракт

`docker_image.web` обеспечивает Nginx image, `docker_container.web` — контейнер `mlops-course-terraform`; HTTP endpoint на 8099 возвращает 200. При повторе plan показывает no-op и detailed exit code 0. Например, смена external 8099→8100 должна быть прочитана как предложенная замена, а не выполнена автоматически по самому факту правки файла. Перед тестом конфигурация и state снова согласованы. Тест строит временный plan, но init/apply/destroy остаются ручными действиями.

## Подготовка и проверка

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

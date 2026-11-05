# Повторяемая инфраструктура

[Модуль](../../README.md) · [Задания](../../README.md#задания) · [Общая подготовка](../../README.md#подготовка-к-заданиям)

## Зачем нужен повторный plan

Успешное создание контейнера показывает только первый переход. Для повторяемой инфраструктуры важно, чтобы повторный запуск с теми же входами не пересоздавал исправный объект. Изменение порта затем показывает, какие свойства provider умеет менять на месте, а какие требуют замены.

В каталоге задания уже есть `main.tf` с Docker provider и loopback-портом. Требуется рабочий Docker daemon. Housing bundle, kind и Vault не используются. Ты изучаешь или меняешь конфигурацию и вручную выполняешь просмотренные действия. Прочти [схему ресурсов](../../README.md#конфигурация-и-реальные-привязки) и [путь plan/apply](../../README.md#путь-init--plan--apply).

## Файл конфигурации и входные параметры

Здесь нет учебной Python-функции. Изучи [main.tf](main.tf), затем применяй просмотренные планы вручную. Во всех трёх заданиях используй этот же каталог.

| Поле или вход | Тип и формат | Происхождение и назначение | Пример |
|---|---|---|---|
| `required_version`, `required_providers.docker` | Ограничения версий HCL | Готовая заготовка фиксирует CLI/provider. Init загружает provider | Terraform `1.11.4`, `kreuzwerker/docker` `3.0.2` |
| `docker_host`, `TF_VAR_docker_host` | Строка endpoint Docker | Из `docker context inspect`. Env переопределяет default `unix:///var/run/docker.sock` | `unix:///путь/к/docker.sock` |
| `docker_image.web.name` | Ссылка Docker image | Фиксированная учебная версия Nginx | `nginx:1.27.5-alpine` |
| `docker_container.web.name` | Строка имени | Имя учебного ресурса Docker, не Terraform address | `mlops-course-terraform` |
| `docker_container.web.image` | Ссылка на `docker_image.web.image_id` | Создаёт зависимость от подготовленного образа | ID image получает provider |
| `ports.internal`, `external`, `ip` | Числа портов и строка IP | Публикация HTTP только на loopback | `80`, `8099`, `127.0.0.1` |
| `output.endpoint` | Строка URL | Выход конфигурации, а не результат curl. При смене порта проверь и его согласованность | `http://127.0.0.1:8099` |
| `MLOPS_TERRAFORM_DIR` | Путь в env pytest | Выбирает уже инициализированный каталог с main.tf и terraform.tfstate | `$PWD/modules/11-terraform/tasks/01-repeat` |

При опыте смены порта редактируй `external` и изучай новый plan. Возврат строки в файле сам не возвращает реальный контейнер: нужно просмотреть и применить новый план. State вручную не исправляй. `course.tfplan` создаёт команда plan, `terraform.tfstate` — применение, `.terraform.lock.hcl` — init. Эти файлы имеют разные роли.

## Технический контракт

`docker_image.web` обеспечивает Nginx image, `docker_container.web` — контейнер `mlops-course-terraform`. HTTP endpoint на 8099 возвращает 200. При повторе plan показывает no-op и detailed exit code 0. Например, смена external 8099→8100 должна быть прочитана как предложенная замена, а не выполнена автоматически по самому факту правки файла. Перед тестом конфигурация и state снова согласованы. Тест строит временный plan, но init/apply/destroy остаются ручными действиями.

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

Ожидается HTTP200. Повторный plan должен показать No changes. Измени внешний порт 8099→8100 и изучи plan: docker_container.web заменяется. Применяй только после просмотра. Верни желаемую конфигурацию и её состояние перед no-op тестом. Тест не применяет plan.

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/01-repeat
```

Рабочий каталог задаётся явно. Нет CLI/provider/state — тест падает с подсказкой. Проверки не выполняют init/apply/destroy и не выводят plan/state. Завершив все три задачи, вручную выполни `terraform -chdir=modules/11-terraform/tasks/01-repeat destroy`, затем удали saved plan. State и plan не коммить.

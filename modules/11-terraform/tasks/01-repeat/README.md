# Создать ресурс и проверить повтор

[Модуль](../../README.md) · [Подготовка](../../README.md#подготовка-к-заданиям) · [Все задания](../../README.md#задания)

## Что предстоит сделать

После ручного запуска web-контейнера возникает вопрос: следующий запуск команды должен создать ещё один экземпляр или использовать существующий? Terraform сопоставляет желаемую конфигурацию с конкретными объектами и показывает действия до их выполнения. Ты применишь готовую конфигурацию, проверишь повтор без изменений и посмотришь, что потребуется при смене порта.

В [main.tf](main.tf) уже описаны Docker image и контейнер. Python-функции здесь нет. Все три задания используют **этот каталог** и его state. Подготовь Docker endpoint по [инструкции модуля](../../README.md#подготовка-к-заданиям). Общий пример `labs/terraform` одновременно не применяй.

## Шаг 1. Связать конфигурацию с ожидаемым результатом

Контейнер отвечает готовой страницей Nginx. Это позволяет наблюдать создание и замену ресурса без зависимости от обучения Housing. В поставке Housing такой ресурс мог бы запускать образ API, но успешное создание контейнера всё равно не заменило бы `/ready` и проверку прогноза.

Различай адрес внутри Terraform и имя во внешней системе. Объявление `docker_container.web` означает управляемый ресурс типа `docker_container` с локальным именем `web`. Его имя в Docker — `mlops-course-terraform`. State после применения свяжет этот адрес с реальным ID. Подробнее — [конфигурация и реальные привязки](../../README.md#конфигурация-и-реальные-привязки).

| Где смотреть в `main.tf` | Что уже задано | Какой результат это определяет |
|---|---|---|
| `required_version`, `required_providers.docker` | CLI `1.11.4`, provider `kreuzwerker/docker` `3.0.2` | `init` выбирает закреплённый плагин работы с Docker API |
| `docker_host` и `provider.docker.host` | Строка адреса daemon | `TF_VAR_docker_host` из подготовки выбирает тот же Docker, что использует CLI |
| `docker_image.web` | `nginx:1.27.5-alpine`, `keep_locally=true` | Подготовленный локальный image. При destroy скачанный image сохраняется |
| `docker_container.web.image` | `docker_image.web.image_id` | Сначала подготовить image, затем создать контейнер из него |
| `ports.internal`, `external`, `ip` | `80`, `8099`, `127.0.0.1` | HTTP контейнера доступен только на loopback-порту компьютера |
| `output.endpoint` | `http://127.0.0.1:8099` | Адрес для клиента. Сам output не делает HTTP-запрос |

Пока ничего менять не нужно. Прочитай [путь init—plan—apply](../../README.md#путь-init--plan--apply), затем выполни его для этого каталога.

## Шаг 2. Применить просмотренный план

Из корня курса:

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat init
terraform -chdir=modules/11-terraform/tasks/01-repeat fmt -check
terraform -chdir=modules/11-terraform/tasks/01-repeat validate
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -out=course.tfplan
```

`init` готовит provider и lock-файл, `validate` проверяет конфигурацию. `plan` читает Docker через provider и предлагает создание. Сначала просмотри адреса и действия: в первый раз ожидаются подготовка image и создание учебного контейнера. Затем примени именно сохранённый план:

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat apply course.tfplan
terraform -chdir=modules/11-terraform/tasks/01-repeat output endpoint
curl -I http://127.0.0.1:8099
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -detailed-exitcode
```

Ожидаются URL, HTTP 200 и `No changes` при повторе. У `-detailed-exitcode` код 0 означает отсутствие действий, 2 — найденные изменения, 1 — ошибку. Файл `course.tfplan` содержит выбранные действия, `terraform.tfstate` — привязки полученных объектов, `.terraform.lock.hcl` — версии/checksums provider. Их назначения различаются.

## Шаг 3. Изучить замену при смене порта

Теперь измени в **этом `main.tf`** `docker_container.web.ports.external` с 8099 на 8100. Измени `output.endpoint`, чтобы он описывал новый адрес. Создай новый plan и посмотри действие для контейнера: выбранный Docker provider требует замену при смене публикации порта. Это удаление и создание с возможным новым ID, а не обновление работающего сокета.

Можно изучить план без применения. Если применяешь его, используй новый saved plan, проверь HTTP на 8100, затем верни обе строки к 8099 и примени просмотренный обратный план. Перед проверкой ниже конфигурация и реальный объект должны снова совпадать. Простая правка файла не возвращает уже изменённый контейнер.

## Проверка и продолжение

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/01-repeat
```

`MLOPS_TERRAFORM_DIR` выбирает существующий инициализированный каталог с `main.tf` и локальным `terraform.tfstate`. Тест строит временный настоящий plan, читает его JSON и требует `actions=["no-op"]` у контейнера и остальных ресурсов, а также код 0. Init/apply/destroy он не выполняет. Без флага live-тест пропущен. Отсутствие CLI/provider/state при включённом флаге — ошибка подготовки.

Оставь контейнер и state для [опыта drift](../02-drift/README.md). State вручную не исправляй. После всех трёх заданий выполни [очистку модуля](../../README.md#остановка-и-очистка). State и saved plan не добавляй в Git.

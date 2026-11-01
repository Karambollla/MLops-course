# Практика: Terraform: инфраструктура как код

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Повтор](tasks/01-repeat/README.md) | [Заготовка](tasks/01-repeat/report.json) · [тесты](tasks/01-repeat/test_task.py) | cpu |
| [Drift](tasks/02-drift/README.md) | [Заготовка](tasks/02-drift/report.json) · [тесты](tasks/02-drift/test_task.py) | cpu |
| [State](tasks/03-state/README.md) | [Заготовка](tasks/03-state/report.json) · [тесты](tasks/03-state/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=11-terraform/01-repeat
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

Нужен Terraform 1.11.4. Проверь `terraform version`. Для Docker Desktop endpoint может отличаться от `/var/run/docker.sock`:

```bash
docker context inspect --format '{{.Endpoints.docker.Host}}'
```

Передай найденное значение через `TF_VAR_docker_host` в своём терминале, без подмены системных переменных.

```bash
terraform -chdir=labs/terraform init
terraform -chdir=labs/terraform fmt -check
terraform -chdir=labs/terraform validate
terraform -chdir=labs/terraform plan -out=course.tfplan
terraform -chdir=labs/terraform apply course.tfplan
curl -I http://127.0.0.1:8099
```

## Завершение

Из той же конфигурации и с тем же Docker endpoint выполни `terraform -chdir=labs/terraform destroy`. Проверь удаление только учебного контейнера. Удали `course.tfplan`, если он больше не нужен; state не добавляй в Git.

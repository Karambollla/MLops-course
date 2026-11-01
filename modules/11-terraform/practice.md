# Практика: Terraform: инфраструктура как код

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Повтор](tasks/01-repeat/README.md) | [Старт](tasks/01-repeat/main.tf) · [Проверка стенда](tasks/01-repeat/test_task.py) | cpu |
| [Drift](tasks/02-drift/README.md) | [Старт](tasks/02-drift/README.md) · [Проверка стенда](tasks/02-drift/test_task.py) | cpu |
| [State](tasks/03-state/README.md) | [Старт](tasks/03-state/README.md) · [Проверка стенда](tasks/03-state/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=11-terraform/01-repeat
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Функции проверяются прямо на фиксированных входах. Live-проверки читают существующий стенд только с MLOPS_RUN_INTEGRATION=1; guides не требуют отдельной сдачи.

## Подготовка

Нужен Terraform 1.11.4. Проверь `terraform version`. Для Docker Desktop endpoint может отличаться от `/var/run/docker.sock`:

```bash
docker context inspect --format '{{.Endpoints.docker.Host}}'
```

Передай найденное значение через `TF_VAR_docker_host` в своём терминале, без подмены системных переменных.

```bash
terraform -chdir=modules/11-terraform/tasks/01-repeat init
terraform -chdir=modules/11-terraform/tasks/01-repeat fmt -check
terraform -chdir=modules/11-terraform/tasks/01-repeat validate
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -out=course.tfplan
terraform -chdir=modules/11-terraform/tasks/01-repeat apply course.tfplan
curl -I http://127.0.0.1:8099
```

## Завершение

Из той же конфигурации и с тем же Docker endpoint выполни `terraform -chdir=modules/11-terraform/tasks/01-repeat destroy`. Проверь удаление только учебного контейнера. Удали `course.tfplan`, если он больше не нужен; state не добавляй в Git.

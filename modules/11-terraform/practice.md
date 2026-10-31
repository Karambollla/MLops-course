# Практика: Terraform: инфраструктура как код

[Теория](README.md) · [Подсказки](hints.md)

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

## Задание 1. Повтор

Повтори plan и сохрани No changes. В конфигурации явно задан `network_mode = "bridge"`: на проверенном Docker 29 неявное значение сети приводило к ложному плану замены контейнера. Не скрывай расхождение через ignore_changes. Измени host port через новую переменную, просмотри plan и объясни update/replacement. Не меняй Docker endpoint, пока исследуешь порт.

## Задание 2. Drift

Удалить разрешено только контейнер `mlops-course-terraform`. Удали его вручную, повтори plan и восстанови через apply. Сравни, что изменила конфигурация и что — ручное действие.

## Задание 3. State

Изучи state через `terraform state list` и `terraform show`. Опиши, что произойдёт при потере state, зачем import и remote backend. Не редактируй JSON state вручную ради прохождения задания.

## Критерии готовности

- [ ] HTTP endpoint реально доступен после apply.
- [ ] Повторный plan не содержит изменений.
- [ ] Drift обнаружен и восстановлен.
- [ ] State, lock-файл и конфигурация различаются по назначению.

## Завершение

Из той же конфигурации и с тем же Docker endpoint выполни `terraform -chdir=labs/terraform destroy`. Проверь удаление только учебного контейнера. Удали `course.tfplan`, если он больше не нужен; state не добавляй в Git.

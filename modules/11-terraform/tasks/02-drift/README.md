# Обнаружение drift

## Зачем менять реальность отдельно от кода

Если внешний оператор удалил объект, неизменённый main.tf ещё не означает исправное окружение. Terraform должен сопоставить сохранённый ID с Docker API и предложить восстановление. Такой разрыв называется drift; потеря файла state была бы другим опытом.

На входе — контейнер и state после задания 01. Все команды продолжают работать с тем же каталогом и Docker endpoint. Новая конфигурация или Python-функция не требуются. Механика разобрана в [повторе, замене и drift](../../README.md#повтор-замена-и-drift).

## Технический контракт

Удаляется только `mlops-course-terraform`, HCL и state не редактируются. Следующий plan должен предложить `create` для `docker_container.web` и завершиться кодом 2. Например, отсутствие контейнера при сохранённом желании его иметь — изменение, а не ошибка планировщика. Live-тест выполняется в этом состоянии до восстановления. После просмотренного apply HTTP снова отвечает 200, а повторный plan становится no-op. Тест не восстанавливает ресурс за тебя.

## Ход опыта

Все три задачи используют **один** каталог `modules/11-terraform/tasks/01-repeat` и его существующий state. Не применяй labs/terraform параллельно с тем же именем контейнера. Terraform 1.11.4/provider 3.0.2 закреплены в main.tf. Docker endpoint узнай через `docker context inspect --format '{{.Endpoints.docker.Host}}'` и задай `TF_VAR_docker_host`.

После задания 01 вручную удали только учебный контейнер:

```bash
docker rm -f mlops-course-terraform
terraform -chdir=modules/11-terraform/tasks/01-repeat plan -detailed-exitcode
```

Ожидается create для docker_container.web и код 2, означающий найденное изменение. Запусти live-тест **до восстановления**. Конфигурацию и state не редактируй ради имитации drift. Затем вручную просмотри plan и выполни apply; HTTP снова 200, следующий plan без изменений. Тест читает настоящий plan и не восстанавливает контейнер.

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_TERRAFORM_DIR="$PWD/modules/11-terraform/tasks/01-repeat" make task TASK=11-terraform/02-drift
```

Рабочий каталог задаётся явно; нет CLI/provider/state — тест падает с подсказкой. Проверки не выполняют init/apply/destroy и не выводят plan/state. Завершив все три задачи, вручную выполни `terraform -chdir=modules/11-terraform/tasks/01-repeat destroy`, затем удали saved plan; state и plan не коммить.

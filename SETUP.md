# Подготовка окружения

Все команды выполняются из корня курса, если явно не указано другое. Не запускай несколько тяжёлых стендов одновременно.

## Основная среда

Нужны Python **3.12**, Git, Docker с Compose v2 или новее, `curl`, `make`. Для Kubernetes нужны `kubectl`, kind **0.27.0**, Helm **3.17.3**. Учебные версии фиксируются в [матрице](docs/versions.md)

Проверь:

```bash
uname -m
python3.12 --version
docker version
docker compose version
docker info --format '{{.Architecture}} {{.MemTotal}}'
```

На Mac с Apple Silicon ожидается `arm64`, на Intel — `x86_64`. Наличие Docker CLI не доказывает доступность daemon: серверная часть `docker version` тоже должна ответить. Открой Docker Desktop или запусти свой Docker runtime.

Для основного проекта используй Python 3.12 и создай **одно** окружение `.venv`. Выбери один из двух способов ниже: через стандартный Python или через `uv`. Если `.venv` уже создана и зависимости установлены, повторно создавать её не нужно — достаточно активировать командой `source .venv/bin/activate`.

### Способ 1: стандартный Python

Установи Python 3.12 через официальный установщик или существующий менеджер версий, затем выполни:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r labs/housing/requirements.txt
python -m pip install --no-deps -e labs/housing
```

Если создание окружения завершилось ошибкой, не переходи к остальным командам: файл активации мог не появиться.

### Способ 2: uv

Если установлен `uv`, вместо команд выше выполни:

```bash
uv python install 3.12
uv venv --python 3.12 --managed-python .venv
source .venv/bin/activate
uv pip install -r labs/housing/requirements.txt
uv pip install --no-deps -e labs/housing
```

### Проверка окружения

После выполнения **одного** из способов проверь установленное окружение:

```bash
make check
make test
```

Для MLflow, DVC, ClearML, ONNX и Qdrant создавай отдельные окружения по инструкциям модулей. Не устанавливай Airflow и GPU serving в основное окружение: у них собственные ограничения зависимостей.

## Переменные окружения и .env

Настройки локальных запусков передаются аргументами CLI или переменными окружения. Например:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 python modules/04-mlflow/tasks/01-experiments/solution.py
```

Файл `.env` — способ сохранить локальные значения, но Python сам его не читает. В курсе нет автоматического загрузчика `.env`: `os.getenv` и `os.environ` получают окружение процесса. Одного создания файла недостаточно для передачи настроек программе. Нужное значение можно задать перед командой, как в примере, или через `export` в терминале.

Compose использует `.env` для подстановок в YAML, а передача переменных контейнеру задаётся через `environment` или `env_file`. Это отдельный механизм: наличие файла не передаёт всё его содержимое в каждый контейнер. В стендах курса нет `env_file` и подстановок `${VAR}`; настройки заданы непосредственно в конфигурациях. Подробности — в [документации Docker Compose](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/).

## Данные и пути

Создай рабочую папку и скачай датасет один раз:

```bash
mkdir -p work
python -m housing.data --output work/housing.csv
```

Первый запуск требует интернет-доступа к источнику California Housing. Скрипт сохраняет CSV и SHA-256; повторные запуски используй с тем же файлом. При недоступности источника остановись и восстанови доступ или скопируй ранее скачанный файл с известной контрольной суммой. Синтетические данные не подменяют реальный датасет при проверке качества. Для DVC отдельно инициализируй Git в собственной рабочей копии, если его ещё нет.

Промежуточные файлы задания сохраняются в его `output/`. Готовые экспортёры обучения и ONNX переносят проверенные результаты в `work/`; команды приведены в [инструкции по заданиям](docs/task-structure.md#результаты-и-перенос).

## Локальный Kubernetes

Установи закреплённые версии инструментов по официальным release pages из [источников](RESOURCES.md). Затем:

```bash
kind create cluster --name mlops-course --image kindest/node:v1.32.2
kubectl config current-context
kubectl get nodes
```

Ожидается контекст `kind-mlops-course` и узел в состоянии Ready. Образ приложения сначала собери и загрузи в kind по модулю 07. Не применяй учебные манифесты в рабочий кластер.

После занятий:

```bash
kind delete cluster --name mlops-course
```

## Жизненный цикл Compose

Пример отдельного стенда:

```bash
docker compose -f labs/mlflow/compose.yaml up -d --build
docker compose -f labs/mlflow/compose.yaml logs --tail=60
docker compose -f labs/mlflow/compose.yaml down
```

Обычный `down` сохраняет именованные volumes. `down -v` удаляет данные только выбранного стенда: выполняй его после экспорта нужных результатов. Не используй глобальную очистку Docker для решения локальной проблемы.

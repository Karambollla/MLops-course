# Практика: Triton Inference Server и перенос модели

[Теория](README.md) · [Подсказки](hints.md)

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Экспорт и ONNX parity](tasks/01-onnx/README.md) | [Заготовка](tasks/01-onnx/solution.py) · [Тесты](tasks/01-onnx/test_task.py) | CPU, включая Mac |
| [HTTP SDK и готовность модели](tasks/02-server/README.md) | [Заготовка](tasks/02-server/solution.py) · [Тесты](tasks/02-server/test_task.py) | клиент CPU; сервер курса Linux x86_64 |
| [Реальные замеры клиента](tasks/03-benchmark/README.md) | [Заготовка](tasks/03-benchmark/solution.py) · [Тесты](tasks/03-benchmark/test_task.py) | клиент CPU; live требует совместимого сервера |

Из корня после SETUP выполняй `make task TASK=15-triton/01-onnx`, подставляя идентификатор темы. Незавершённые student функции дают NotImplementedError. Базовая коллекция не требует необязательных SDK; `MLOPS_RUN_SDK=1` включает SDK tests, `MLOPS_RUN_INTEGRATION=1` — уже работающий внешний сервис. `make test` проверяет готовые инструменты курса, задания запускаются отдельно.

## Окружения клиента и экспорта

`labs/triton/requirements.txt` сохраняет CPU ONNX-export зависимости и не тянет Triton client в Mac-окружение автоматически. Для HTTP SDK используй отдельное окружение с базовыми зависимостями курса (как в SETUP):

```bash
python3.12 -m venv .venv-triton-client
source .venv-triton-client/bin/activate
python -m pip install -r labs/housing/requirements.txt
python -m pip install -e labs/housing
python -m pip install -r labs/triton/client-requirements.txt
python -m pip install -r labs/triton/requirements.txt
python -c 'import tritonclient.http; import onnxruntime; print("HTTP client and ORT imported")'
MLOPS_RUN_SDK=1 make task TASK=15-triton/02-server
```

ONNX/ORT в client env нужны для synthetic SDK parity test и live-сравнения с локальной моделью. Экспортировать Pipeline можно в основном Mac export env. Client package `tritonclient[http]==2.59.0` действительно импортирован на Darwin arm64 / Python 3.12.16; ограничение Linux x86_64 относится к выбранному **серверному** compose-стенду. У [релиза PyPI 2.59.0](https://pypi.org/project/tritonclient/2.59.0/#files) есть универсальный Python wheel; совместимость его transitive native dependencies с другой версией Python/OS проверь установкой/import smoke, не выводи её из платформ сервера.

SDK test задания 02 вызывает student infer с настоящими SDK tensor/result types и tiny synthetic ONNX/ORT. Он подменяет transport boundary без сетевого сервиса и не является live inference. Студенческие `feature_matrix` и `infer` нужно реализовать; готовый ответ не вложен в тестовую фикстуру. Сервер не заменяется fake endpoint.

## Живой сервер и результат

Экспортируй свой housing Pipeline через задание 01, затем `python modules/15-triton/tasks/01-onnx/export.py`. На совместимом Linux x86_64 стенде:

```bash
docker compose -f labs/triton/compose.yaml up -d
MLOPS_RUN_INTEGRATION=1 TRITON_URL=http://127.0.0.1:8000 make task TASK=15-triton/02-server
python scripts/run_task.py run 15-triton/02-server --rows work/triton/rows.json
python scripts/run_task.py run 15-triton/03-benchmark --rows work/triton/rows.json --requests 200 --warmup 5 --output work/triton/benchmark.json
```

В rows.json нужен JSON-список объектов с восемью числовыми housing features в именованных полях, без target; возьми реальные строки своих данных. CLI inference отправляет FP32 `[N,8]` и печатает модель и named outputs с shape/dtype/числами. Live test проверяет server/model readiness и сравнивает student SDK outputs с тем же файлом ONNX через ORT. Старый read-only HTTP probe сохранён. Иной локальный путь модели задаёт `TRITON_ONNX_PATH`; файл должен совпадать с моделью сервера.

Benchmark CLI после warmup измеряет последовательные настоящие вызовы клиента, сохраняет сырые rows и elapsed_seconds, затем считает summary по ним. Тесты не разворачивают сервисы, не экспортируют модель и не готовят work автоматически. При включённом opt-in недостающая зависимость, модель или сервер — ошибка. Реального server inference на несовместимой машине не предполагается; успешный SDK import его не доказывает.

## Завершение

`docker compose -f labs/triton/compose.yaml down` на серверном стенде. Сохрани ONNX/hash/manifest и исходные benchmark данные вне Git. Для Mac/client-пути деактивируй отдельное окружение командой `deactivate`.

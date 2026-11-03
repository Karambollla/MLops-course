# Версии и совместимость

Выбраны конкретные учебные релизы с доступными API и примерами. Это не список последних релизов. Смена версии — отдельный эксперимент с повторной проверкой зависимостей и лабораторных.

| Компонент | Учебная версия | Среда |
|---|---|---|
| Python | 3.12.12 | Основной код; Docker base `python:3.12.12-slim` |
| NumPy / pandas / scikit-learn | 2.2.6 / 2.2.3 / 1.6.1 | CPU, Python 3.12 |
| FastAPI / Uvicorn | 0.115.12 / 0.34.2 | Основной API |
| pytest / httpx | 8.3.5 / 0.28.1 | Тесты |
| ipykernel / Matplotlib | 6.29.5 / 3.10.3 | Первая ячейка ML-notebook, интерактивное ядро и графики |
| MLflow / SQLAlchemy | 3.1.1 / 2.0.41 | SDK и server; SQLAlchemy 2.1 несовместим с этим MLflow |
| ClearML Server / Agent | 1.16.1 / 1.9.3 | Server Linux x86_64; Agent в собственном venv |
| DVC / ClearML SDK | 3.59.2 / 1.18.0 | Отдельные окружения |
| Airflow | 3.1.0-python3.12 | Standalone image; учебный SQLite |
| kind / Kubernetes node / Helm | 0.27.0 / 1.32.2 / 3.17.3 | Локальный кластер |
| Prometheus / Grafana | 3.2.1 / 11.6.0 | Compose |
| Vault / Terraform | 1.19.0 / 1.11.4 | Локальные лабораторные |
| Terraform Docker provider | 3.0.2 | Lock-файл создаётся `terraform init` |
| Ansible core | 2.18.4 | Контроллер внутри Python Docker-образа |
| Qdrant / Python client | 1.13.6 / 1.13.3 | Локальная небольшая коллекция |
| Elasticsearch / OpenSearch | 8.17.3 / 2.19.1 | Раздельные CPU-стенды |
| ONNX / skl2onnx / ONNX Runtime | 1.17.0 / 1.18.0 / 1.22.0 | Экспорт в отдельном окружении |
| Triton / TensorRT-LLM image | 25.06-py3 / 25.06-trtllm-python-py3 | Дополнительный Linux/NVIDIA стенд |
| vLLM / SGLang image | v0.10.2 / v0.4.10.post2-cu126 | Дополнительный Linux/NVIDIA стенд |

Точные прямые Python-зависимости закреплены в requirements-файлах; дополнительные зависимости ML-notebook — в его первой ячейке. Для основного проекта также включён сгенерированный lock всех транзитивных зависимостей; результаты проверок описаны в [проверках курса](verification.md). Для MLflow Server также сохранён полный lock в `labs/mlflow/server.txt`. Для остальных стендов базовый образ или собственный набор требований изолирует окружение, но транзитивные зависимости могут изменяться при пересборке: после успешной лабораторной сохрани `pip freeze`, image digest и lock-файлы вместе с результатами запуска. Теги не равнозначны immutable digest.

Перед запуском образа на ARM64 выполни `docker buildx imagetools inspect IMAGE:TAG`. Для отсутствующей платформы в модуле указан дополнительный путь; не считать эмуляцию доказанной совместимостью. Проверенные и непроверенные случаи перечислены в [проверках курса](verification.md).

Для NVIDIA-стенда сопоставь версию драйвера, CUDA, GPU compute capability, backend и модель по release notes именно закреплённого образа. Не смешивай TensorRT engine от одного релиза с другим без повторной сборки. Таблица NVIDIA: [release compatibility](https://docs.nvidia.com/deeplearning/triton-inference-server/archives/triton-inference-server-2590/user-guide/docs/introduction/compatibility.html).

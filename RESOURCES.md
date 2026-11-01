# Каталог материалов

Сначала читай собственную теорию модуля, затем нужные разделы первоисточника. Бесплатная доступность страниц не требует покупки курсов.

## Как пользоваться

Официальная документация — источник API и требований к версиям. Внешние курсы помогают понять процесс, но команды из старых занятий сверяй с выбранным релизом. Для закреплённых лабораторных предпочитай versioned docs; latest-страницы полезны для концепций и проверки изменений. Не нужно читать документацию целиком до первой практики.

## 00. Python для Go-разработчика

[Перейти к модулю](modules/00-python/README.md).

- [Python Tutorial](https://docs.python.org/3.12/tutorial/) — разделы Data Structures, Errors and Exceptions, Modules; читать после собственных примеров.
- [NumPy fundamentals](https://numpy.org/doc/stable/user/basics.html) — shape, dtype, indexing и broadcasting; воспроизвести маленькие массивы.
- [pandas getting started](https://pandas.pydata.org/docs/getting_started/intro_tutorials/) — чтение таблиц, выбор строк и преобразования; не учить весь API наизусть.

## 01. ML и оценка моделей

[Перейти к модулю](modules/01-ml/README.md).

- [California Housing](https://scikit-learn.org/stable/datasets/real_world.html#california-housing-dataset) — описание признаков, единицы target и происхождение данных.
- [Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) — inconsistent preprocessing, data leakage, random state.
- [Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html) — regression metrics и ограничения сравнения.
- [FSDL course](https://fullstackdeeplearning.com/course/2022/) — лекции о lifecycle, testing и deployment; использовать концепции, не копировать старые команды установки.

## 02. Воспроизводимость, данные и DVC

[Перейти к модулю](modules/02-reproducibility/README.md).

- [DVC get started](https://dvc.org/doc/start) — data management, local remote и восстановление версий.
- [DVC pipelines](https://dvc.org/doc/start/data-pipelines) — deps, outs и воспроизведение шагов.
- [sklearn model persistence](https://scikit-learn.org/stable/model_persistence.html) — совместимость и ограничения pickle/joblib/ONNX.

## 03. ML-сервис, Docker и CI

[Перейти к модулю](modules/03-service-ci/README.md).

- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) — TestClient, assertions и проверка HTTP-контракта.
- [FastAPI deployment](https://fastapi.tiangolo.com/deployment/concepts/) — startup, workers, память и репликация.
- [Docker workshop](https://docs.docker.com/get-started/workshop/) — image, container, volume и Compose.
- [GitHub Actions Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) — проверки Python в workflow.

## 04. MLflow: эксперименты и реестр моделей

[Перейти к модулю](modules/04-mlflow/README.md).

- [MLflow Tracking](https://mlflow.org/docs/3.1.1/ml/tracking/) — manual logging, tracking server и stores; если URL перенаправляет, выбери версию 3.1.1.
- [MLflow Registry](https://mlflow.org/docs/3.1.1/ml/model-registry/) — registered models, versions и aliases.
- [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/02-experiment-tracking) — дополнительный разбор экспериментов; адаптировать команды под закреплённый SDK.

## 05. Airflow: оркестрация ML-пайплайнов

[Перейти к модулю](modules/05-airflow/README.md).

- [Airflow Docker 3.1.0](https://airflow.apache.org/docs/apache-airflow/3.1.0/howto/docker-compose/index.html) — требования к Docker, память и границы учебного стенда.
- [Airflow tutorials](https://airflow.apache.org/docs/apache-airflow/3.1.0/tutorial/index.html) — TaskFlow и устройство DAG.
- [Airflow best practices](https://airflow.apache.org/docs/apache-airflow/3.1.0/best-practices.html) — идемпотентность, top-level code и передача данных.

## 06. ClearML: задачи, артефакты и агенты

[Перейти к модулю](modules/06-clearml/README.md).

- [ClearML first steps](https://clear.ml/docs/latest/docs/getting_started/main/) — Task, experiment management и remote execution.
- [ClearML offline mode](https://clear.ml/docs/latest/docs/guides/set_offline/) — локальные сессии и их импорт; отличать от очереди.
- [ClearML Server](https://clear.ml/docs/latest/docs/deploying_clearml/clearml_server/) — компоненты server и требования к самостоятельному развёртыванию.

## 07. Kubernetes: выкладка и диагностика

[Перейти к модулю](modules/07-kubernetes/README.md).

- [Kubernetes basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/) — Deployment, Service, scaling и updates.
- [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) — различие liveness/readiness/startup.
- [Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) — requests, limits и OOM.
- [kind quick start](https://kind.sigs.k8s.io/docs/user/quick-start/) — локальный кластер и загрузка images.

## 08. Helm: воспроизводимые релизы

[Перейти к модулю](modules/08-helm/README.md).

- [Helm quickstart](https://helm.sh/docs/v3/intro/quickstart/) — базовые install/upgrade/rollback для Helm 3.
- [Chart template guide](https://helm.sh/docs/v3/chart_template_guide/) — values, quoting, flow control и debugging.

## 09. Prometheus, Grafana и качество модели

[Перейти к модулю](modules/09-monitoring/README.md).

- [Prometheus first steps](https://prometheus.io/docs/introduction/first_steps/) — scrape, expression browser и targets.
- [Prometheus querying](https://prometheus.io/docs/prometheus/latest/querying/basics/) — labels, selectors и временные диапазоны.
- [Grafana getting started](https://grafana.com/docs/grafana/latest/fundamentals/getting-started/) — datasource, panels и dashboards.
- [Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) — pending/firing и for.

## 10. Vault: секреты и жизненный цикл доступа

[Перейти к модулю](modules/10-vault/README.md).

- [Vault getting started](https://developer.hashicorp.com/vault/tutorials/get-started) — dev server, auth, secrets и policy.
- [KV v2](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2) — версионирование и API paths.
- [Kubernetes auth](https://developer.hashicorp.com/vault/docs/auth/kubernetes) — identity Pod и выдача ограниченных token.

## 11. Terraform: инфраструктура как код

[Перейти к модулю](modules/11-terraform/README.md).

- [Terraform Docker tutorials](https://developer.hashicorp.com/terraform/tutorials/docker-get-started) — локальные create/change/destroy без облака.
- [Terraform state](https://developer.hashicorp.com/terraform/language/state) — назначение state, locking и чувствительные значения.
- [Docker provider](https://registry.terraform.io/providers/kreuzwerker/docker/3.0.2/docs) — схема ресурсов и Docker host.

## 12. Ansible: настройка и идемпотентность

[Перейти к модулю](modules/12-ansible/README.md).

- [Ansible getting started](https://docs.ansible.com/projects/ansible/latest/getting_started/index.html) — inventory, playbook и modules.
- [Handlers](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html) — notify и порядок выполнения.
- [Check mode](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html) — возможности и ограничения check/diff.

## 13. Qdrant и основы векторного поиска

[Перейти к модулю](modules/13-qdrant/README.md).

- [Qdrant quickstart](https://qdrant.tech/documentation/quickstart/) — collections, upsert и query_points.
- [Qdrant filtering](https://qdrant.tech/documentation/concepts/filtering/) — payload filters и условия.
- [FastEmbed](https://qdrant.tech/documentation/fastembed/) — CPU embeddings и поддерживаемые модели.
- [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5) — размерность, назначение, preprocessing и условия модели.

## 14. Elasticsearch и OpenSearch: сравнение поиска

[Перейти к модулю](modules/14-elasticsearch-opensearch/README.md).

- [Elasticsearch kNN](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/knn-search.html) — dense_vector и knn query выбранной версии.
- [Elasticsearch bulk](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/docs-bulk.html) — NDJSON и per-item errors.
- [OpenSearch vector search](https://docs.opensearch.org/docs/2.19/vector-search/) — knn_vector, engines и запросы.
- [OpenSearch Docker](https://docs.opensearch.org/docs/2.19/install-and-configure/install-opensearch/docker/) — ресурсы и Linux sysctl для локального запуска.

## 15. Triton Inference Server и перенос модели

[Перейти к модулю](modules/15-triton/README.md).

- [Triton architecture](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/architecture.html) — backend, scheduler и model instances.
- [Model configuration](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_configuration.html) — dims, batch и input/output.
- [skl2onnx tutorial](https://onnx.ai/sklearn-onnx/) — поддерживаемые converters и initial_types.
- [ONNX Runtime Python](https://onnxruntime.ai/docs/get-started/with-python.html) — InferenceSession и локальная проверка.

## 16. vLLM, SGLang и TensorRT-LLM

[Перейти к модулю](modules/16-llm-serving/README.md).

- [vLLM documentation](https://docs.vllm.ai/en/v0.10.2/) — версия лабораторной: serving, metrics и installation.
- [SGLang repository](https://github.com/sgl-project/sglang/tree/v0.4.10.post2) — README и docs именно выбранного тега; latest CLI может отличаться.
- [TensorRT-LLM backend 25.06](https://docs.nvidia.com/deeplearning/triton-inference-server/archives/triton-inference-server-2560/user-guide/docs/tensorrtllm_backend/README.html) — conversion, engine и model repository релиза 25.06.
- [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) — архитектура, лицензия, tokenizer и ограничения маленькой модели.

## 17. Подготовка к собеседованиям и защита проекта

[Перейти к модулю](modules/17-career/README.md).

- [Google ML engineering rules](https://developers.google.com/machine-learning/guides/rules-of-ml) — практические вопросы качества данных, простого baseline и эксплуатации.
- [FSDL course](https://fullstackdeeplearning.com/course/2022/) — повторить lifecycle, testing и deployment перед защитой.

## Окружение и версии инструментов

- [Python downloads](https://www.python.org/downloads/) — Python 3.12 и установщик своей платформы.
- [uv documentation](https://docs.astral.sh/uv/) — необязательная установка Python и изоляция окружений.
- [kind v0.27.0](https://github.com/kubernetes-sigs/kind/releases/tag/v0.27.0) — закреплённый CLI и совместимые node images.
- [Helm v3.17.3](https://github.com/helm/helm/releases/tag/v3.17.3) — бинарник своей архитектуры и checksum.
- [Terraform 1.11.4](https://releases.hashicorp.com/terraform/1.11.4/) — бинарник и контрольные суммы.

## Аналоги курсов

- [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) — дополнительные домашние задания по tracking, orchestration, deployment, monitoring. Начни с соответствующего раздела после собственного модуля.
- [Full Stack Deep Learning 2022](https://fullstackdeeplearning.com/course/2022/) — полезен для системного взгляда на данные, testing и deployment; не используется как актуальная инструкция установки библиотек.

Объяснения и задания курса написаны самостоятельно. Источники перечислены для углубления и проверки технических деталей; длинные тексты из чужих материалов не копируются.

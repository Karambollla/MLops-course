# Практика инструментов по темам

Это карта действий и критериев приёмки, а не список уже выполненных учащимся лабораторных. [Статус проверок](verification.md) отделяет выполненные smoke-проверки SDK от незавершённых учебных функций.

`make task TASK=<ID>` запускает все тестовые файлы темы. Локальные SDK-проверки включаются `MLOPS_RUN_SDK=1`; чтение живых стендов — `MLOPS_RUN_INTEGRATION=1`. Создание учебных ресурсов и генерация нагрузки требуют дополнительно `MLOPS_RUN_WRITES=1`; такие тесты используют marker `writes`. Пропуск теста не является выполнением задания. GPU/LLM API не имитируются.

## ML-notebook

| Раздел | Инструмент и самостоятельная работа | Вход → выход | Проверка |
|---|---|---|---|
| [Baseline](../modules/01-ml/housing.ipynb) | scikit-learn: split, метрики, DummyRegressor | CSV → индексы и ошибки baseline | Ячейки notebook на CPU |
| [Кандидат](../modules/01-ml/housing.ipynb) | Pipeline: сравнение по validation и train | CSV/config → bundle/metrics/manifest/split | Ячейки, сериализация и повтор |
| [Анализ ошибок](../modules/01-ml/housing.ipynb) | pandas/NumPy: группы и география | Test predictions/targets → ошибки по группам | Ячейки, без использования test для подбора |

## Темы каталога

| Тема | Инструмент | Что реализовать или изменить | Вход → выход | Проверка результата | Среда |
|---|---|---|---|---|---|
| [00-python/01-records](../modules/00-python/tasks/01-records/README.md) | Python | Фильтрация и агрегирование записей | Словари → count/mean | Чистые функции | CPU |
| [00-python/02-jsonl-cli](../modules/00-python/tasks/02-jsonl-cli/README.md) | Python CLI | Построчное чтение и обработка ошибок | JSONL → один JSON или stderr/exit code | CLI и функции | CPU |
| [00-python/03-tabular-analysis](../modules/00-python/tasks/03-tabular-analysis/README.md) | pandas/NumPy | Анализ и выравнивание таблиц | CSV/Series → сводка и согласованные строки | Настоящие pandas/NumPy | CPU |
| [02-reproducibility/01-data-version](../modules/02-reproducibility/tasks/01-data-version/README.md) | DVC CLI | Версионирование, push/pull и проверка восстановления | CSV → локальный remote → те же bytes/SHA-256 | Локальный DVC + функции учащегося | CPU, отдельный venv |
| [02-reproducibility/02-manifest](../modules/02-reproducibility/tasks/02-manifest/README.md) | Python + Pipeline | Проверка происхождения реальной модели | CSV/bundle → manifest или отказ схемы | Файлы и Pipeline из notebook | CPU |
| [02-reproducibility/03-reproduce](../modules/02-reproducibility/tasks/03-reproduce/README.md) | joblib/scikit-learn | Сравнение двух собственных запусков | Bundles/метрики → различия происхождения и прогнозов | Настоящая загрузка Pipeline | CPU |
| [03-service-ci/01-api-contract](../modules/03-service-ci/tasks/01-api-contract/README.md) | FastAPI TestClient | Проверка API собственной модели | HTTP batch → predictions/version/validation errors | Настоящий FastAPI и Pipeline | CPU |
| [03-service-ci/02-container](../modules/03-service-ci/tasks/02-container/README.md) | Docker CLI/HTTP | Сборка и запуск API | Image + bundle → HTTP readiness/predict | Живой контейнер | Docker |
| [03-service-ci/03-ci](../modules/03-service-ci/tasks/03-ci/README.md) | GitHub Actions | Настройка workflow проверок | Commit → результаты jobs | Запуск workflow в собственной копии | GitHub, руководство |
| [04-mlflow/01-experiments](../modules/04-mlflow/tasks/01-experiments/README.md) | mlflow SDK | Обучение и запись трёх runs | CSV/config → params/metrics/artifacts | Локальный SDK и живой tracking server | CPU/Docker |
| [04-mlflow/02-registry](../modules/04-mlflow/tasks/02-registry/README.md) | MlflowClient/sklearn flavor | Регистрация и закрепление версии | Pipeline/run → model version/signature/predict | Registry и численный паритет | CPU/Docker |
| [04-mlflow/03-outage](../modules/04-mlflow/tasks/03-outage/README.md) | MLflow Registry | Восстановление регистрации без дублей | Сохранённый state → та же версия модели | Реестр после отказа и retry | Docker |
| [05-airflow/01-pipeline](../modules/05-airflow/tasks/01-pipeline/README.md) | airflow.sdk | Построение и исполнение DAG | CSV → обучение → файлы/XCom metadata | Реальные task instances | Docker/Airflow |
| [05-airflow/02-gate-retry](../modules/05-airflow/tasks/02-gate-retry/README.md) | Airflow tasks | Подключение gate и идемпотентной публикации | Метрики → допуск/отказ → release | DAG, downstream status и release | Docker/Airflow |
| [05-airflow/03-failure-intervals](../modules/05-airflow/tasks/03-failure-intervals/README.md) | Airflow context/timetable | Интервалы и retry упавшего шага | Data interval + artifacts → повтор без дубля | Task attempts, XCom и файлы | Docker/Airflow |
| [06-clearml/01-offline](../modules/06-clearml/tasks/01-offline/README.md) | ClearML SDK | Запись результатов настоящего обучения | CSV → Task params/metrics/artifacts | Настоящая offline Task и её архив | CPU, отдельный venv |
| [06-clearml/02-agent](../modules/06-clearml/tasks/02-agent/README.md) | ClearML Task/Agent | Передача обучения в очередь | Task → queue → Agent → результат | Server Task/логи/артефакты | Совместимый Server/Agent |
| [06-clearml/03-comparison-failure](../modules/06-clearml/tasks/03-comparison-failure/README.md) | ClearML/MLflow/Airflow | Сравнение границ и восстановление исполнения | Реальные состояния запусков → объяснимый выбор | Наблюдение UI/логов, руководство | Совместимый стенд |
| [07-kubernetes/01-unready](../modules/07-kubernetes/tasks/01-unready/README.md) | kubectl/Deployment | Ресурсы, probes и запуск без модели | Manifest → running/unready Pod | Живой API Kubernetes и HTTP | kind |
| [07-kubernetes/02-release](../modules/07-kubernetes/tasks/02-release/README.md) | kubectl/Service | Выкладка модели и проверка Service | Image/bundle → ready Pod/predict | Deployment endpoints и HTTP | kind |
| [07-kubernetes/03-failure](../modules/07-kubernetes/tasks/03-failure/README.md) | kubectl rollout | Отказ и откат | Неудачный rollout → прежняя версия | Rollout history и predict | kind, руководство |
| [08-helm/01-values](../modules/08-helm/tasks/01-values/README.md) | Helm CLI | Параметризация и установка chart | Chart/values → rendered manifests/release | Lint/template и живой release | kind/Helm |
| [08-helm/02-rollback](../modules/08-helm/tasks/02-rollback/README.md) | Helm upgrade/rollback | Неудачный upgrade и восстановление модели | Release revisions → working model_version | История release и HTTP | kind/Helm, руководство |
| [09-monitoring/01-load-dashboard](../modules/09-monitoring/tasks/01-load-dashboard/README.md) | HTTP + prometheus_client + Grafana | Нагрузка, PromQL и dashboard | predict-запросы → timestamps/counters/panels | measure_load и scrape Prometheus | Docker |
| [09-monitoring/02-outage](../modules/09-monitoring/tasks/02-outage/README.md) | Prometheus alerts | Правила и обнаружение отказа | Остановленный API → target down/alert | Живые targets и alert rules | Docker |
| [09-monitoring/03-quality-drift](../modules/09-monitoring/tasks/03-quality-drift/README.md) | pandas/NumPy | Сопоставление predictions/targets и drift | Реальные сохранённые строки → MAE/drift | Вычисления по ID, без выдуманного качества | CPU |
| [10-vault/01-policy](../modules/10-vault/tasks/01-policy/README.md) | hvac/Vault KV v2 | Ограниченное чтение и policy | Token + path → field_present или Forbidden | Настоящий Vault, без вывода секрета | Docker |
| [10-vault/02-expiry](../modules/10-vault/tasks/02-expiry/README.md) | hvac/Vault token API | Renew/revoke и классификация отказов | Собственный token → доступ/истечение/отзыв | Состояние token и повторное чтение | Docker |
| [10-vault/03-integration](../modules/10-vault/tasks/03-integration/README.md) | Vault auth/CLI | Выдача доступа приложению | Policy/auth → ограниченный доступ Pod | Права и жизненный цикл доступа | kind/Vault, руководство |
| [11-terraform/01-repeat](../modules/11-terraform/tasks/01-repeat/README.md) | Terraform Docker provider | Создание и повторное применение | HCL → реальные Docker-ресурсы/state | apply и plan без изменений | Docker/Terraform |
| [11-terraform/02-drift](../modules/11-terraform/tasks/02-drift/README.md) | Terraform CLI | Обнаружение и устранение drift | Удалённый ресурс → plan/apply → восстановление | Настоящий provider и HTTP | Docker/Terraform |
| [11-terraform/03-state](../modules/11-terraform/tasks/03-state/README.md) | Terraform state/plan | Связь state и ресурсов | State/config → обнаруженные различия | CLI и реальные ресурсы | Docker/Terraform |
| [12-ansible/01-idempotency](../modules/12-ansible/tasks/01-idempotency/README.md) | Ansible CLI | Два исполнения своего playbook | Inventory/playbook → recap и настройка Linux | Реальный контейнер и changed=0 | Docker/Ansible |
| [12-ansible/02-template-handler](../modules/12-ansible/tasks/02-template-handler/README.md) | Ansible template/handler | Изменение конфигурации и handler | Template → файл → уведомление handler | Реальный playbook и endpoint | Docker/Ansible |
| [12-ansible/03-tool-boundaries](../modules/12-ansible/tasks/03-tool-boundaries/README.md) | Terraform/Ansible | Разделение владения ресурсами и конфигурацией | Практика предыдущих тем → выбор инструмента | Руководство без фиктивных тестов | CPU |
| [13-qdrant/01-plumbing](../modules/13-qdrant/tasks/01-plumbing/README.md) | qdrant-client | Коллекция, upsert, query/filter | Корпус/вектор → points/payload/hits | In-memory SDK и живой Qdrant | CPU/Docker |
| [13-qdrant/02-evaluation](../modules/13-qdrant/tasks/02-evaluation/README.md) | Метрики + Qdrant hits | Оценка фактической выдачи | IDs из SDK + qrels → Recall/Precision/MRR | Чистая функция и реальные hits | CPU/Docker |
| [13-qdrant/03-embeddings](../modules/13-qdrant/tasks/03-embeddings/README.md) | CPU encoder/qdrant-client | Вычисление embeddings и версия индекса | Тексты/локальная модель → vectors/manifest | Geometry/hash и реальный encoder | CPU, скачивание весов явно |
| [14-elasticsearch-opensearch/01-elasticsearch](../modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/README.md) | elasticsearch SDK | Индекс, bulk и lexical/vector search | Корпус/mapping → документы и hits | SDK против живого Elasticsearch | Docker, отдельный venv |
| [14-elasticsearch-opensearch/02-opensearch](../modules/14-elasticsearch-opensearch/tasks/02-opensearch/README.md) | opensearch-py | Собственный mapping и kNN/filter | Корпус/mapping → документы и hits | SDK против живого OpenSearch | Docker, по очереди с ES |
| [14-elasticsearch-opensearch/03-comparison](../modules/14-elasticsearch-opensearch/tasks/03-comparison/README.md) | SDK hits + RRF | Объединение и оценка реальных выдач | Lexical/vector IDs + qrels → hybrid ranking/метрики | RRF и результаты клиентов | CPU/Docker |
| [15-triton/01-onnx](../modules/15-triton/tasks/01-onnx/README.md) | skl2onnx/ONNX Runtime | Экспорт и паритет модели | Собственный Pipeline → ONNX graph/predictions | Настоящие библиотеки, 100 строк | CPU |
| [15-triton/02-server](../modules/15-triton/tasks/02-server/README.md) | tritonclient.http | Подготовка tensor и inference | Batch → InferInput → response/as_numpy | Живой Triton и ONNX Runtime parity | Совместимый Triton runtime |
| [15-triton/03-benchmark](../modules/15-triton/tasks/03-benchmark/README.md) | tritonclient + monotonic clock | Реальная серия inference | Запросы → сырые latency/status/elapsed → summary | Клиентские измерения работающего сервера | Совместимый Triton runtime |
| [16-llm-serving/01-memory-contract](../modules/16-llm-serving/tasks/01-memory-contract/README.md) | Локальные вычисления | Память/KV cache и разбор готовых SSE | Числа/подготовленные события → расчёты | Без LLM API; не интеграция | CPU |
| [16-llm-serving/02-engines](../modules/16-llm-serving/tasks/02-engines/README.md) | Локальные метрики | TTFT/TPOT по подготовленным событиям | Timestamps/content → метрики | Генерация/streaming/benchmark API пропущены | CPU; API вне практики |
| [16-llm-serving/03-tensorrt](../modules/16-llm-serving/tasks/03-tensorrt/README.md) | Архитектура TensorRT-LLM | Путь checkpoint → engine → serving | Описание конфигурации → понимание компонентов | API генерации пропущен | Теория, без LLM endpoints |
| [17-career/01-defense](../modules/17-career/tasks/01-defense/README.md) | Архитектура проекта | Демонстрация измеренного результата | Собственный проект → примеры рассказа | Рекомендации, без отчёта/баллов | Руководство |
| [17-career/02-interview](../modules/17-career/tasks/02-interview/README.md) | Инженерные решения | Объяснение практики и отказов | Собственный опыт → технические ответы | Рекомендации и примеры | Руководство |
| [17-career/03-resume](../modules/17-career/tasks/03-resume/README.md) | Портфолио | Описание подтверждённого опыта | Измеренные результаты → формулировки резюме | Без выдуманных достижений | Руководство |

## Исключённые API-сценарии

В `16-llm-serving/02-engines` не выполняются API-клиент генерации, streaming и нагрузочные запросы vLLM/SGLang. В `16-llm-serving/03-tensorrt` не выполняются API генерации TensorRT-LLM и соответствующего Triton backend. Необязательная генеративная часть [поискового проекта](../projects/search/README.md#необязательный-rag) также пропущена. Ни облачные, ни локальные, ни удалённые LLM endpoints не вызываются. Локальное кодирование текста в embeddings не является вызовом LLM API.

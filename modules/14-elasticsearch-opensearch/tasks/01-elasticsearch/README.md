# Elasticsearch: bulk и ошибки

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## Какую проблему решает bulk

Нужно загрузить корпус без дубликатов и заметить частичный отказ. У bulk-запроса может быть HTTP 200, хотя отдельный документ отвергнут. [NDJSON и уровни ошибок](../../README.md#bulk-и-два-уровня-ошибок) объясняют, почему контракт требует проверять items.

Предоставлены корпус `labs/search/corpus.json`, запросы/qrels, [mapping.json](mapping.json), `solution.py` и CPU Compose Elasticsearch 8.17.3. Нужны [основное окружение](../../../../SETUP.md) и выполненный модуль 13. Другие тяжёлые стенды и любой сервис на host port 9200 останови до запуска.

## Контракты

`build_bulk(documents,index) -> str` сохраняет исходные IDs в `_id` (строка), формирует пары action/source и завершающий `\n`. Source содержит только text/topic/vector. Пустой index и повтор ID — ValueError. `bulk_failures(response) -> list[str]` проверяет каждый item: status>=300 или поле error означает отказ, даже если HTTP 200 и верхний errors=False. На OpenSearch перенеси свою реализацию этих двух функций из первого задания.

Новые SDK-функции — заготовки с NotImplementedError:

- `ensure_index(client,index,mapping) -> None`: через indices.exists/create создай отсутствующий индекс; для существующего сравни text/topic/vector и векторные настройки через get_mapping/get_settings. Не удаляй его; несовместимость — ValueError до ingest. Повторный вызов безопасен.
- `ingest_documents(client,index,documents) -> int`: отправь build_bulk через client.bulk, передай ответ в bulk_failures, при любом отказе выброси ValueError с IDs. Успех — refresh и число успешно загруженных документов. Не полагайся на count или errors вместо items; тело с text-объектом вместо строки даёт настоящий mapper error для ID900 в live-тесте. Повторная загрузка тех же IDs сохраняет count=8.
- `lexical_search(client,index,text,k=5,topic=None) -> list[dict]`: match по text, size=k, необязательный term по topic внутри query. Пустой text или неверный k — ValueError.
- `vector_search(client,index,vector,k=2,topic=None,dimension=4) -> list[dict]`: настоящий client.search с нативным kNN и фильтром внутри поиска. Параметры вектора проверяются до сети как в knn_request. В Elasticsearch num_candidates>=k (на этом корпусе достаточно max(8,k)); OpenSearch использует knn_request.

Оба поиска возвращают список в порядке движка: `{id:int, score:float, payload:{text,topic}}`. IDs нормализуются обратно в int для qrels/RRF. Нет совпадений — []. Переданный client принадлежит вызывающему коду, функции его не закрывают. SDK самостоятельно сериализует запросы: не отправляй HTTP вручную вместо заданных методов.

## Запуск

Все команды из корня курса в отдельном Python 3.12 окружении после SETUP:

```bash
python -m pip install -r labs/search/requirements.txt
docker compose -f labs/search/elasticsearch.compose.yaml up -d
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py --help
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py index --url http://127.0.0.1:9200 --index course-docs
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py lexical --text Vault
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py vector --vector 0 0 0 1 --k 2 --topic security
make task TASK=14-elasticsearch-opensearch/01-elasticsearch
```

CLI уже разбирает параметры, создаёт `Elasticsearch` и вызывает функции; SDK-операции реализуешь сам. Исходная заготовка даёт NotImplementedError. `--mapping`, `--corpus`, `--index`, `--url` выбирают вход загрузки; `--k`, `--dimension`, `--topic` задают поиск. Elasticsearch client 8.17.2 и opensearch-py 2.8.0 закреплены в requirements. Без SDK сбор тестов и --help работают; отсутствующий транзитивный dependency не маскируется как отсутствие SDK.

Ожидаемое поведение настоящей практики: после двух ingest count=8 и payload сохранён, match Vault включает ID7, kNN security возвращает IDs 7/8, неизвестный topic даёт []. Неверная размерность отклоняется до SDK. Live-тест вызывает твою реализацию, затем читает созданный ею индекс и передаёт реальные выдачи в `ranking_metrics` модуля 13 и RRF задания 03: сначала реализуй эти функции.

```bash
# Запись только в уникальное тестовое имя; cleanup удаляет только это имя.
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 ELASTICSEARCH_URL=http://127.0.0.1:9200 python scripts/run_task.py test 14-elasticsearch-opensearch/01-elasticsearch -- -m writes
# Прежний read-only probe: course-docs должен быть уже подготовлен.
MLOPS_RUN_INTEGRATION=1 ELASTICSEARCH_URL=http://127.0.0.1:9200 python scripts/run_task.py test 14-elasticsearch-opensearch/01-elasticsearch -- -m 'integration and not writes'
```

Записывающий тест требует оба флага, отмечен integration/writes, генерирует UUID-имя и проверяет его отсутствие до работы. Он проверяет mapping, повторный ingest, каждый слой поиска, ошибку bulk item, метрики и RRF; finally удаляет только своё имя. Без флагов он пропускается; при включении недоступный сервер, SDK или незавершённая функция — ошибка, а не skip. Прежний probe только читает course-docs; он не доказывает, что твой импорт работает.

Останови активный Compose через down перед запуском другого движка: оба используют host port 9200. Volume сохраняется. Обязательного текстового отчёта нет. Эти команды описывают проверку после реализации; доступность твоего endpoint заранее не предполагается.

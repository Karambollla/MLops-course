# Elasticsearch: bulk и ошибки

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## Какую проблему решает bulk

Нужно загрузить корпус без дубликатов и заметить частичный отказ. У bulk-запроса может быть HTTP 200, хотя отдельный документ отвергнут. [NDJSON и уровни ошибок](../../README.md#bulk-и-два-уровня-ошибок) объясняют, почему контракт требует проверять items.

Предоставлены корпус `labs/search/corpus.json`, запросы/qrels, [mapping.json](mapping.json), `solution.py` и CPU Compose Elasticsearch 8.17.3. Нужны [основное окружение](../../../../SETUP.md) и выполненный модуль 13. Другие тяжёлые стенды и любой сервис на host port 9200 останови до запуска.

## Что реализовать

`build_bulk(documents,index) -> str` формирует пары строк action/document и завершающий перевод строки. Action — `index` с `_index` и `_id` строкой из исходного ID; document содержит `text`, `topic`, `vector`. Пустое имя индекса и повтор ID внутри корпуса вызывают ValueError. Повторный вызов с теми же данными даёт те же IDs.

`bulk_failures(response) -> list[str]` возвращает IDs операций с status>=300 либо error, проверяя каждый item. Ответ с единственным item `_id:"2",status:400,error:{...}` должен дать `["2"]`; успешный status=201 без error — пустой список. HTTP-код всего запроса не подменяет эту проверку.

Для ID=1 и index=course-docs первая строка результата — `{"index":{"_index":"course-docs","_id":"1"}}`, вторая содержит поля документа. Это NDJSON, без внешних квадратных скобок. Отдельного CLI у заготовки нет: транспорт загрузки и поиска выполняй своим клиентом после реализации функций, не меняя их сигнатур.

## Подготовить и проверить индекс

Все команды из корня курса:

```bash
docker compose -f labs/search/elasticsearch.compose.yaml up -d
curl --fail http://127.0.0.1:9200
curl --fail -X PUT http://127.0.0.1:9200/course-docs -H 'Content-Type: application/json' --data-binary @modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/mapping.json
make task TASK=14-elasticsearch-opensearch/01-elasticsearch
```

PUT выполняется для нового индекса; `resource_already_exists_exception` означает существующий индекс, а не необходимость скрыть ошибку. Сверь его mapping перед повторным использованием. Загрузи NDJSON в `/_bulk` с `application/x-ndjson`, проверь items, затем видимость через refresh. Повторный ingest исходного корпуса должен оставить count=8.

Выполни match по слову Vault и kNN по `[0,0,0,1]` с k=2/num_candidates=8. Ожидаются ID7 среди lexical hits и набор 7/8 для kNN. Сохрани top-5, scores и время своих запросов в `work/`. Форма kNN и значения параметров разобраны [здесь](../../README.md#два-разных-knn-запроса); scores — не вероятности и не обязаны совпадать с Qdrant.

```bash
MLOPS_RUN_INTEGRATION=1 ELASTICSEARCH_URL=http://127.0.0.1:9200 make task TASK=14-elasticsearch-opensearch/01-elasticsearch
```

Probe только читает count и делает search по уже подготовленному индексу, не создаёт/удаляет его. Без opt-in он пропущен, unit-тесты функций работают. При opt-in отсутствие URL/сервера/индекса — ошибка. Проверяется ожидаемое поведение корпуса, а не latency или качество настоящих embeddings.

## Завершение

Сохрани mapping, корпус, qrels и исходные измерения. Останови `docker compose -f labs/search/elasticsearch.compose.yaml down` перед OpenSearch. Volume останется. Обязательный письменный отчёт не нужен.

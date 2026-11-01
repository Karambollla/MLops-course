# OpenSearch: собственный kNN-запрос

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## Почему нужен отдельный запрос

Корпус остаётся прежним, но новый движок иначе описывает векторное поле и поиск. Нужно отделить предметные параметры — vector, k, topic — от wire-формата OpenSearch. Различия mapping и запросов разобраны в [схеме](../../README.md#mapping-и-путь-документа) и [двух kNN-запросах](../../README.md#два-разных-knn-запроса).

Уже предоставлены `solution.py`, [mapping.json](mapping.json), корпус/queries из `labs/search/` и CPU Compose OpenSearch 2.19.1. Нужны [основное окружение](../../../../SETUP.md) и понимание ingest предыдущего задания. Готовый Elasticsearch JSON не является входом этой функции.

## Технический контракт

Реализуй `knn_request(vector,k,topic=None,dimension=4) -> dict`. На верхнем уровне `size=k`, затем `query.knn.vector` содержит координаты в `vector` и число соседей в `k`. Здесь внешний vector — имя поля mapping. Если topic задан, внутри этого объекта добавляется `filter:{term:{topic:значение}}`. Не используй post_filter.

k — положительное integer без bool; число координат равно dimension; вектор конечный и не нулевой. Неверный k, размерность, NaN/infinity и нулевой вектор вызывают ValueError до HTTP. Для новой embedding-модели dimension передаётся явно из её версии индекса, а не угадывается.

Например, вход `[0,0,0,1]`, k=2, topic=security даёт size=2 и фильтр по точному keyword topic внутри knn-запроса. Отправка этого тела подготовленному серверу должна вернуть IDs `"7"`/`"8"` с topic=security. Формирование словаря и реальная отправка — разные шаги; unit-тест проверяет первый, opt-in probe — второй.

## Подготовка стенда

```bash
docker compose -f labs/search/elasticsearch.compose.yaml down
docker compose -f labs/search/opensearch.compose.yaml up -d
curl --fail http://127.0.0.1:9200
curl --fail -X PUT http://127.0.0.1:9200/course-docs -H 'Content-Type: application/json' --data-binary @modules/14-elasticsearch-opensearch/tasks/02-opensearch/mapping.json
```

Команды выполняются из корня курса. Mapping выбирает Lucene HNSW, cosine и четыре координаты; именно этот engine поддерживает используемый фильтр. Если индекс уже существует, проверь схему до загрузки. Загрузи те же восемь документов со стабильными `_id`, проверь каждый bulk item и refresh. Можно повторно использовать подготовку NDJSON, но не переносить Elasticsearch kNN JSON.

Если сервис не стартует, смотри `docker compose -f labs/search/opensearch.compose.yaml logs opensearch`; `vm.max_map_count` настраивается в Linux runtime. Диагностика ресурсов — в [теории](../../README.md#ресурсы-и-диагностика-стенда).

## Проверка

```bash
make task TASK=14-elasticsearch-opensearch/02-opensearch
MLOPS_RUN_INTEGRATION=1 OPENSEARCH_URL=http://127.0.0.1:9200 make task TASK=14-elasticsearch-opensearch/02-opensearch
```

CLI отсутствует; первая команда вызывает функцию тестами, незавершённая заготовка даёт NotImplementedError. Вторая отправляет результат твоей `knn_request` реальному OpenSearch. Probe ожидает count=8, IDs 7/8 с фильтром security и ID7 в match по Vault. Он только читает индекс; не готовит и не удаляет его. Без opt-in серверная проверка пропускается, при включении отсутствие URL/сервера/индекса — ошибка.

Сохрани исходные выдачи с теми же queries и k для следующего сравнения. После работы выполни `docker compose -f labs/search/opensearch.compose.yaml down`; данные volume сохранятся. Письменный отчёт не требуется.

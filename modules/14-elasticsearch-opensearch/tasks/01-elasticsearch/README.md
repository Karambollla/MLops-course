# Elasticsearch: bulk и ошибки

[Модуль и подготовка](../../README.md#подготовка-к-заданиям) · [Все задания модуля](../../README.md#задания) · [Окружение курса](../../../../SETUP.md)

## Какую проблему решает bulk

Нужно загрузить корпус без дубликатов и заметить частичный отказ. У bulk-запроса может быть HTTP 200, хотя отдельный документ отвергнут. [NDJSON и уровни ошибок](../../README.md#bulk-и-два-уровня-ошибок) объясняют, почему контракт требует проверять items.

Реализуй шесть учебных функций в соседнем [solution.py](solution.py). `main()` с клиентом и разбором CLI уже готов. Предоставлены корпус `labs/search/corpus.json`, запросы/qrels, [mapping.json](mapping.json), `solution.py` и CPU Compose Elasticsearch 8.17.3. Нужны [основное окружение](../../../../SETUP.md) и выполненный модуль 13. Другие тяжёлые стенды и любой сервис на host port 9200 останови до запуска.

## Документы, mapping и клиент

`documents` в функциях ниже — JSON-массив из `labs/search/corpus.json`, уже декодированный через `json.loads`. ID 7 в этом корпусе назначен инструкции о политиках Vault, ID 8 — credentials. Один документ имеет вид `{"id":7,"text":"Vault policies restrict secrets","topic":"security","vector":[0,0,0,1]}`. Файл с запросами содержит отдельные `vector` и `relevant`: разметка не загружается в индекс.

`client` — уже созданный объект SDK `Elasticsearch`. CLI создаёт его по `--url` и закрывает в `finally`. Учебные функции используют переданный клиент и не закрывают его. Не заменяй SDK-вызовы самостоятельными HTTP-запросами.

[Mapping](mapping.json) загружается целиком как `dict`, включая верхние `mappings`. Поле `text` типа `text` анализируется для лексического поиска. `topic` типа `keyword` используется для точного фильтра. `vector` имеет тип `dense_vector`, `dims=4`, `index=true`, `similarity=cosine`.

## Шаг 1. Подготовить bulk и проверить его результат

### `build_bulk(documents: list[dict], index: str) -> str`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `documents` | `list[dict]` | Документы с устойчивыми `id`, `text`, `topic`, `vector` | Декодированный корпус или маленький тестовый список | `[{"id":7,"text":"Vault","topic":"security","vector":[0,0,0,1]}]` |
| `index` | `str` | Непустое имя целевого индекса | CLI `--index` или уникальное имя теста | `"course-docs"` |

Верни строку NDJSON из пар action/source, с завершающим переводом строки. Для одного документа форма такая:

```text
{"index":{"_index":"course-docs","_id":"7"}}
{"text":"Vault","topic":"security","vector":[0,0,0,1]}
```

После второй строки нужен `\n`. Это две JSON-строки, а не JSON-массив. `_id` — строка исходного ID, source содержит только `text`, `topic`, `vector`. Экранируй переводы строк в тексте через JSON-сериализацию, чтобы один документ не разорвал NDJSON. Пустое имя индекса и повтор ID вызывают `ValueError`. Сама функция ничего не отправляет серверу.

### `bulk_failures(response: dict) -> list[str]`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `response` | `dict` по сигнатуре | Декодированный ответ bulk с массивом `items`. Каждый item содержит результат операции | Результат `client.bulk` | `{"errors":False,"items":[{"index":{"_id":"7","status":400}}]}` |

Для примера верни `["7"]`. Каждый item со `status>=300` или полем `error` считается неуспешным независимо от верхнего `errors`. Пустые items и полностью успешные операции дают `[]`. Сохрани порядок отказов. В Elasticsearch ответ может быть `ObjectApiResponse`: читай `response["items"]`, используя его интерфейс отображения.

## Шаг 2. Проверить схему и загрузить документы

### `ensure_index(client, index: str, mapping: dict) -> None`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | Elasticsearch | Установленное SDK-соединение с выбранным сервером | CLI или вызывающий код | `Elasticsearch("http://127.0.0.1:9200")` |
| `index` | `str` | Имя создаваемого или проверяемого индекса | CLI `--index` | `"course-docs"` |
| `mapping` | `dict` | Полное содержимое mapping-файла этого задания | `json.loads(Path(...).read_text())`, CLI `--mapping` | `{"mappings":{"properties":{...}}}` |

Используй `indices.exists/create` для отсутствующего индекса. Для существующего прочитай `get_mapping/get_settings` и сверь `text`, `topic`, `vector` и векторные настройки. У Elasticsearch проверь в частности `dims`, `index` и `similarity` поля `vector`. Несовместимость вызывает `ValueError` до ingest. Нельзя удалять существующий индекс. При успехе верни `None`, повторный вызов не должен менять документы.

### `ingest_documents(client, index: str, documents: list[dict]) -> int`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | Elasticsearch | Клиент для настоящих `bulk` и `indices.refresh` | CLI или вызывающий код | Уже созданный SDK-клиент |
| `index` | `str` | Имя индекса с совместимым mapping | Результат подготовки через `ensure_index` | `"course-docs"` |
| `documents` | `list[dict]` | Документы для загрузки с исходными IDs | JSON-корпус, CLI `--corpus` | Восемь объектов из `corpus.json` |

Передай NDJSON из `build_bulk` в `client.bulk`, разбери каждый item через `bulk_failures`. Любой отказ вызывает `ValueError`, в сообщении должны быть IDs отвергнутых документов. Успех требует refresh и возвращает число загруженных документов, для корпуса — `8`. Два ingest исходных IDs оставляют count=8.

Bulk не является транзакцией: ошибка одного item не откатывает успешные items. Для проверки отказа live-тест создаёт отдельный неверный документ с новым ID 900 с объектом вместо строкового `text` и ожидает настоящую mapper error с ID 900 в исключении. `HTTP 200`, поле `errors` или итоговый count по отдельности не заменяют разбор каждого item.

## Шаг 3. Выполнить два вида поиска

### `lexical_search(client, index: str, text: str, k: int = 5, topic: str | None = None) -> list[dict]`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | Elasticsearch | Клиент для `search` | CLI или вызывающий код | Уже созданный SDK-клиент |
| `index` | `str` | Индекс с загруженными документами | Тот же `--index`, что при ingest | `"course-docs"` |
| `text` | `str` | Непустой текст для `match` по полю `text` | Пользовательский запрос или CLI `--text` | `"Vault"` |
| `k` | `int` | Положительное число hits без `bool` | Параметр функции или CLI `--k` | `5` |
| `topic` | `str` или `None` | Точный `term`-фильтр внутри query | Категория корпуса, CLI `--topic` | `"security"` |

Отправь `match` по text и `size=k` через `client.search`. Необязательный topic ограничивает сам запрос. Пустой text или неверный k дают `ValueError`. Запрос Vault должен включать ID 7, тот же запрос с topic=release даёт `[]`.

### `vector_search(client, index: str, vector: list[float], k: int = 2, topic: str | None = None, dimension: int = 4) -> list[dict]`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | Elasticsearch | Клиент для нативного kNN через `search` | CLI или вызывающий код | Уже созданный SDK-клиент |
| `index` | `str` | Индекс с векторами нужной схемы | Тот же `--index`, что при ingest | `"course-docs"` |
| `vector` | `list[float]` | Конечный ненулевой вектор длины `dimension` | Запрос из `queries.json` или CLI `--vector` | `[0,0,0,1]` |
| `k` | `int` | Положительное число соседей без `bool` | CLI `--k` | `2` |
| `topic` | `str` или `None` | Точное ограничение по теме, до top-k | CLI `--topic` | `"security"` |
| `dimension` | `int` | Положительная размерность без `bool`, согласованная с mapping | Версия индекса, CLI `--dimension` | `4` |

Неверные `k`, `dimension`, длина, конечность или норма вектора дают `ValueError` до обращения к сети. Используй нативный Elasticsearch kNN с `num_candidates>=k`. Для корпуса достаточно `max(8,k)`. Фильтр помещается в kNN-запрос, а не после top-k.

Оба поиска разбирают `hits.hits` и возвращают список в порядке движка. Форма одного результата: `{"id":7,"score":0.9,"payload":{"text":"...","topic":"security"}}`. Score приведён только как пример типа: у движков разные шкалы. Преобразуй `_id` обратно в `int` для qrels и RRF. Для security-вектора ожидаются IDs 7 и 8 с topic=security. Нет совпадений или topic неизвестен — `[]`.

## Готовый CLI

`main()` уже читает файлы, создаёт SDK-клиент и закрывает его. Выбери обязательное действие: `index`, `lexical` или `vector`.

| Аргумент | Формат и назначение | По умолчанию |
|---|---|---|
| `--url` | HTTP-адрес выбранного сервера | `http://127.0.0.1:9200` |
| `--index` | Имя индекса для любой операции | `course-docs` |
| `--corpus` | Путь к JSON-массиву документов для `index` | `labs/search/corpus.json` |
| `--mapping` | Путь к JSON с полным mapping для `index` | `mapping.json` рядом с solution.py |
| `--text` | Текст для `lexical` | `Vault` |
| `--vector` | Координаты через пробел для `vector` | `0 0 0 1` |
| `--k` | Максимум hits. CLI явно передаёт его и в lexical | `2` |
| `--dimension` | Ожидаемая размерность запроса | `4` |
| `--topic` | Точная категория поиска | Без фильтра |

При `index` CLI печатает число успешно загруженных документов, при поиске — JSON-список hits. Значение `k=5` относится к прямому вызову `lexical_search` без аргумента k. CLI использует свой default `2`.

## Проверить реализацию

Сначала проверь чистые функции из корня курса в окружении [подготовки](../../README.md#подготовка-к-заданиям):

```bash
make task TASK=14-elasticsearch-opensearch/01-elasticsearch
```

Затем запусти Elasticsearch. OpenSearch на этом порту должен быть остановлен.

```bash
docker compose -f labs/search/elasticsearch.compose.yaml up -d
curl --fail http://127.0.0.1:9200
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py index
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py index
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py lexical --text Vault
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py vector --vector 0 0 0 1 --k 2 --topic security
```

Каждый `index` должен напечатать `8`, а в индексе после повтора остаются восемь документов. Лексический поиск включает ID 7 (Vault), векторный возвращает IDs 7/8 (Vault и credentials). Payload берётся из `_source`. Неизвестный topic даёт `[]`, неверная размерность — `ValueError` до SDK. Незавершённые функции дают `NotImplementedError`.

Теперь реализуй `ranking_metrics` из 13/02 и RRF из задания 03, чтобы серверный тест мог проверить выдачу целиком:

```bash
# Запись только в уникальное тестовое имя; cleanup удаляет только это имя.
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 ELASTICSEARCH_URL=http://127.0.0.1:9200 python scripts/run_task.py test 14-elasticsearch-opensearch/01-elasticsearch -- -m writes
# Read-only probe: course-docs должен быть уже подготовлен.
MLOPS_RUN_INTEGRATION=1 ELASTICSEARCH_URL=http://127.0.0.1:9200 python scripts/run_task.py test 14-elasticsearch-opensearch/01-elasticsearch -- -m 'integration and not writes'
```

Первый тест использует новое UUID-имя и вызывает твои функции: проверяет mapping, два импорта, поиск, отказ неверного документа, метрики и RRF. После выполнения удаляет только свой индекс. Второй читает заранее подготовленный `course-docs` прямым HTTP. Для записи нужны оба флага. Без них соответствующие проверки пропускаются. При включении отсутствие SDK, сервера или реализации даёт ошибку.

## Остановка

```bash
docker compose -f labs/search/elasticsearch.compose.yaml down
```

Volume сохраняется. Перед запуском другого движка освободи порт 9200.

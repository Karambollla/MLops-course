# OpenSearch: собственный kNN-запрос

[Модуль и подготовка](../../README.md#подготовка-к-заданиям) · [Все задания модуля](../../README.md#задания) · [Окружение курса](../../../../SETUP.md)

## Почему нужен отдельный запрос

Корпус остаётся прежним, но новый движок иначе описывает векторное поле и поиск. Нужно отделить предметные параметры — vector, k, topic — от wire-формата OpenSearch. Различия mapping и запросов разобраны в [схеме](../../README.md#mapping-и-путь-документа) и [двух kNN-запросах](../../README.md#два-разных-knn-запроса).

Уже предоставлены `solution.py`, [mapping.json](mapping.json), корпус/queries из `labs/search/` и CPU Compose OpenSearch 2.19.1. Нужны [основное окружение](../../../../SETUP.md) и понимание ingest предыдущего задания. Готовый Elasticsearch JSON не является входом этой функции.

## Документы, mapping и клиент

`documents` в функциях ниже — JSON-массив из `labs/search/corpus.json`, уже декодированный через `json.loads`. Один документ имеет вид `{"id":7,"text":"Vault policies restrict secrets","topic":"security","vector":[0,0,0,1]}`. Файл с запросами содержит отдельные `vector` и `relevant`: разметка не загружается в индекс.

`client` — уже созданный объект SDK `OpenSearch`. CLI создаёт его по `--url` и закрывает в `finally`. Учебные функции используют переданный клиент и не закрывают его. Не заменяй SDK-вызовы самостоятельными HTTP-запросами.

[Mapping](mapping.json) загружается целиком как `dict`, включая верхние `mappings` и `settings`. Поле `text` типа `text` анализируется для лексического поиска. `topic` типа `keyword` используется для точного фильтра. `vector` имеет тип `knn_vector`, `dimension=4`, метод `hnsw`, `engine=lucene`, `space_type=cosinesimil`. `settings.index.knn=true` включает kNN для индекса.

## Функции и их входы

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

Для примера верни `["7"]`. Каждый item со `status>=300` или полем `error` считается неуспешным независимо от верхнего `errors`. Пустые items и полностью успешные операции дают `[]`. Сохрани порядок отказов. В OpenSearch перенеси свою проверенную реализацию из первого задания.

### `ensure_index(client, index: str, mapping: dict) -> None`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | OpenSearch | Установленное SDK-соединение с выбранным сервером | CLI или вызывающий код | `OpenSearch("http://127.0.0.1:9200")` |
| `index` | `str` | Имя создаваемого или проверяемого индекса | CLI `--index` | `"course-docs"` |
| `mapping` | `dict` | Полное содержимое mapping-файла этого задания | `json.loads(Path(...).read_text())`, CLI `--mapping` | `{"mappings":{"properties":{...}}}` |

Используй `indices.exists/create` для отсутствующего индекса. Для существующего прочитай `get_mapping/get_settings` и сверь `text`, `topic`, `vector` и векторные настройки. У OpenSearch проверь также `index.knn`: SDK может вернуть `True` или строку `"true"`. Несовместимость вызывает `ValueError` до ingest. Нельзя удалять существующий индекс. При успехе верни `None`, повторный вызов не должен менять документы.

### `ingest_documents(client, index: str, documents: list[dict]) -> int`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | OpenSearch | Клиент для настоящих `bulk` и `indices.refresh` | CLI или вызывающий код | Уже созданный SDK-клиент |
| `index` | `str` | Имя индекса с совместимым mapping | Результат подготовки через `ensure_index` | `"course-docs"` |
| `documents` | `list[dict]` | Документы для загрузки с исходными IDs | JSON-корпус, CLI `--corpus` | Восемь объектов из `corpus.json` |

Передай NDJSON из `build_bulk` в `client.bulk`, разбери каждый item через `bulk_failures`. Любой отказ вызывает `ValueError`, в сообщении должны быть IDs отвергнутых документов. Успех требует refresh и возвращает число загруженных документов, для корпуса — `8`. Два ingest исходных IDs оставляют count=8.

Bulk не является транзакцией: ошибка одного item не откатывает успешные items. Live-тест посылает ID900 с объектом вместо строкового `text` и ожидает настоящую mapper error с ID900 в исключении. `HTTP 200`, поле `errors` или итоговый count по отдельности не заменяют разбор каждого item.

### `lexical_search(client, index: str, text: str, k: int = 5, topic: str | None = None) -> list[dict]`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | OpenSearch | Клиент для `search` | CLI или вызывающий код | Уже созданный SDK-клиент |
| `index` | `str` | Индекс с загруженными документами | Тот же `--index`, что при ingest | `"course-docs"` |
| `text` | `str` | Непустой текст для `match` по полю `text` | Пользовательский запрос или CLI `--text` | `"Vault"` |
| `k` | `int` | Положительное число hits без `bool` | Параметр функции или CLI `--k` | `5` |
| `topic` | `str` или `None` | Точный `term`-фильтр внутри query | Категория корпуса, CLI `--topic` | `"security"` |

Отправь `match` по text и `size=k` через `client.search`. Необязательный topic ограничивает сам запрос. Пустой text или неверный k дают `ValueError`. Запрос Vault должен включать ID7, тот же запрос с topic=release даёт `[]`.

### `vector_search(client, index: str, vector: list[float], k: int = 2, topic: str | None = None, dimension: int = 4) -> list[dict]`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `client` | OpenSearch | Клиент для нативного kNN через `search` | CLI или вызывающий код | Уже созданный SDK-клиент |
| `index` | `str` | Индекс с векторами нужной схемы | Тот же `--index`, что при ingest | `"course-docs"` |
| `vector` | `list[float]` | Конечный ненулевой вектор длины `dimension` | Запрос из `queries.json` или CLI `--vector` | `[0,0,0,1]` |
| `k` | `int` | Положительное число соседей без `bool` | CLI `--k` | `2` |
| `topic` | `str` или `None` | Точное ограничение по теме, до top-k | CLI `--topic` | `"security"` |
| `dimension` | `int` | Положительная размерность без `bool`, согласованная с mapping | Версия индекса, CLI `--dimension` | `4` |

Неверные `k`, `dimension`, длина, конечность или норма вектора дают `ValueError` до обращения к сети. Строй запрос через свою `knn_request`, описанную ниже.

Оба поиска разбирают `hits.hits` и возвращают список в порядке движка. Форма одного результата: `{"id":7,"score":0.9,"payload":{"text":"...","topic":"security"}}`. Score приведён только как пример типа: у движков разные шкалы. Преобразуй `_id` обратно в `int` для qrels и RRF. Для security-вектора ожидаются IDs 7 и 8 с topic=security. Нет совпадений или topic неизвестен — `[]`.

### `knn_request(vector: list[float], k: int, topic: str | None = None, dimension: int = 4) -> dict`

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `vector` | `list[float]` | Координаты запроса длины `dimension`, конечные и ненулевые | Тот же вектор, что передан в `vector_search` | `[0,0,0,1]` |
| `k` | `int` | Положительное число соседей, без `bool` | Аргумент поиска | `2` |
| `topic` | `str` или `None` | Точный фильтр, `None` означает отсутствие фильтра | Аргумент поиска | `"security"` |
| `dimension` | `int` | Положительная ожидаемая длина, без `bool` | Mapping индекса | `4` |

Функция только строит JSON-объект и не вызывает сеть. Для указанных входов форма результата:

```json
{"size":2,"query":{"knn":{"vector":{"vector":[0,0,0,1],"k":2,"filter":{"term":{"topic":"security"}}}}}}
```

Внешний `vector` — имя поля mapping. Внутренний `vector` — координаты. Без topic ключ filter не нужен. `post_filter` недопустим. Неправильная геометрия, k или dimension дают `ValueError` до SDK. Этот формат относится к OpenSearch с Lucene HNSW, его нельзя копировать в Elasticsearch.

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

## Запуск

Все команды из корня курса в отдельном Python 3.12 окружении после SETUP:

```bash
python -m pip install -r labs/search/requirements.txt
docker compose -f labs/search/elasticsearch.compose.yaml down
docker compose -f labs/search/opensearch.compose.yaml up -d
python modules/14-elasticsearch-opensearch/tasks/02-opensearch/solution.py --help
python modules/14-elasticsearch-opensearch/tasks/02-opensearch/solution.py index --url http://127.0.0.1:9200 --index course-docs
python modules/14-elasticsearch-opensearch/tasks/02-opensearch/solution.py lexical --text Vault
python modules/14-elasticsearch-opensearch/tasks/02-opensearch/solution.py vector --vector 0 0 0 1 --k 2 --topic security
make task TASK=14-elasticsearch-opensearch/02-opensearch
```

CLI уже разбирает параметры, создаёт `OpenSearch` и вызывает функции. SDK-операции реализуешь сам. Исходная заготовка даёт NotImplementedError. `--mapping`, `--corpus`, `--index`, `--url` выбирают вход загрузки. `--k`, `--dimension`, `--topic` задают поиск. Elasticsearch client 8.17.2 и opensearch-py 2.8.0 закреплены в requirements. Без SDK сбор тестов и --help работают. Отсутствующий транзитивный dependency не маскируется как отсутствие SDK.

Ожидаемое поведение настоящей практики: после двух ingest count=8 и payload сохранён, match Vault включает ID7, kNN security возвращает IDs 7/8, неизвестный topic даёт []. Неверная размерность отклоняется до SDK. Live-тест вызывает твою реализацию, затем читает созданный ею индекс и передаёт реальные выдачи в `ranking_metrics` модуля 13 и RRF задания 03: сначала реализуй эти функции.

```bash
# Запись только в уникальное тестовое имя; cleanup удаляет только это имя.
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 OPENSEARCH_URL=http://127.0.0.1:9200 python scripts/run_task.py test 14-elasticsearch-opensearch/02-opensearch -- -m writes
# Read-only probe: course-docs должен быть уже подготовлен.
MLOPS_RUN_INTEGRATION=1 OPENSEARCH_URL=http://127.0.0.1:9200 python scripts/run_task.py test 14-elasticsearch-opensearch/02-opensearch -- -m 'integration and not writes'
```

Записывающий тест требует оба флага, отмечен integration/writes, генерирует UUID-имя и проверяет его отсутствие до работы. Он проверяет mapping, повторный ingest, каждый слой поиска, ошибку bulk item, метрики и RRF. Finally удаляет только своё имя. Без флагов он пропускается. При включении недоступный сервер, SDK или незавершённая функция — ошибка, а не skip. Read-only probe только читает course-docs. Он не доказывает, что твой импорт работает.

## Остановка

```bash
docker compose -f labs/search/opensearch.compose.yaml down
```

Volume сохраняется. Перед запуском другого движка освободи порт 9200.

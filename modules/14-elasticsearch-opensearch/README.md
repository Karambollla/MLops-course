# 14. Elasticsearch и OpenSearch: сравнение поиска

[Программа](../../README.md) · [Задания](#задания) · [Подготовка](#подготовка-к-заданиям)

## Какую задачу решает модуль

В [модуле Qdrant](../13-qdrant/README.md) поиск вернул ближайшие векторы. Теперь пользователь ищет точное имя `Vault`, код ошибки или перефразированную инструкцию. Один способ ранжирования не обязан одинаково хорошо обслуживать все случаи. Нужно сравнить текстовый и векторный сигналы на одних данных, а затем объединить результаты прозрачным правилом.

Используются те же восемь документов, четыре запроса и relevant IDs из `labs/search/`. Поэтому предметная сущность остаётся прежней: документ — инструкция, запрос — информационная потребность, релевантность — независимая разметка подходящих инструкций. Нужны HTTP/JSON, понимание embeddings и метрик из модуля 13. Локальные CPU-стенды закреплены на Elasticsearch 8.17.3 и OpenSearch 2.19.1. Они запускаются последовательно: оба публикуют порт 9200.

Elasticsearch и OpenSearch — отдельные поисковые системы. У них похожие HTTP API и общее происхождение, но настройки векторов и запросы нельзя считать взаимозаменяемыми. Здесь embeddings вычислены заранее: облачные semantic endpoints не нужны.

## Подготовка к заданиям

Все команды выполняются из корня курса. Для функций NDJSON, RRF и проверки запроса достаточно [основной среды](../../SETUP.md#основная-среда). Для работы с SDK создай отдельное Python 3.12 окружение:

```bash
python3.12 -m venv .venv-search
source .venv-search/bin/activate
python -m pip install -r labs/housing/requirements.txt
python -m pip install --no-deps -e labs/housing
python -m pip install -r labs/search/requirements.txt
```

В requirements закреплены `elasticsearch==8.17.2` и `opensearch-py==2.8.0`. Серверы запускаются Docker Compose и не устанавливаются через pip. Используй [корпус](../../labs/search/corpus.json) и [queries/qrels](../../labs/search/queries.json) модуля 13. Для записывающих тестов нужны также готовые `ranking_metrics` из 13/02 и RRF из задания 03 этого модуля.

| Файл или настройка | Elasticsearch | OpenSearch |
|---|---|---|
| Compose | [elasticsearch.compose.yaml](../../labs/search/elasticsearch.compose.yaml) | [opensearch.compose.yaml](../../labs/search/opensearch.compose.yaml) |
| Сервер | `8.17.3` | `2.19.1` |
| Mapping задания | [mapping.json](tasks/01-elasticsearch/mapping.json) | [mapping.json](tasks/02-opensearch/mapping.json) |
| JVM heap | `ES_JAVA_OPTS: -Xms768m -Xmx768m` | `OPENSEARCH_JAVA_OPTS: -Xms768m -Xmx768m` |
| Данные | Volume `elastic-data` | Volume `opensearch-data` |

Оба сервера используют `discovery.type: single-node`, host port `127.0.0.1:9200` и лимит памяти контейнера 2g. Heap не занимает всю разрешённую память, поскольку процессу нужны native memory и файловый cache. В Elasticsearch `xpack.security.enabled=false` отключает security. В OpenSearch это делают `DISABLE_INSTALL_DEMO_CONFIG=true` и `DISABLE_SECURITY_PLUGIN=true`. Эти настройки относятся к локальному учебному стенду.

Останови Qdrant, ClearML и другие тяжёлые стенды. Запускай Elasticsearch и OpenSearch последовательно, поскольку они занимают один порт. Начни с Elasticsearch:

```bash
docker compose -f labs/search/elasticsearch.compose.yaml up -d
curl --fail http://127.0.0.1:9200
```

Дождись успешного JSON-ответа сервера. При ошибке посмотри `docker compose -f labs/search/elasticsearch.compose.yaml logs --tail=60`. Bootstrap-ошибка `vm.max_map_count` относится к Linux runtime Docker, а не mapping документа. Загрузку корпуса выполняй своим CLI первого задания после реализации функций.

Перед OpenSearch останови Elasticsearch и только затем запускай второй стенд:

```bash
docker compose -f labs/search/elasticsearch.compose.yaml down
docker compose -f labs/search/opensearch.compose.yaml up -d
curl --fail http://127.0.0.1:9200
```

## Задания

| Задание | Что выполнить | Файлы и среда |
|---|---|---|
| [01. Elasticsearch](tasks/01-elasticsearch/README.md) | NDJSON, проверка всех bulk items, создание mapping и SDK-поиск | [solution.py](tasks/01-elasticsearch/solution.py) · [Тесты](tasks/01-elasticsearch/test_task.py). CPU и отдельный сервер |
| [02. OpenSearch](tasks/02-opensearch/README.md) | Построить нативный kNN-запрос и повторить SDK-путь на том же корпусе | [solution.py](tasks/02-opensearch/solution.py) · [Тесты](tasks/02-opensearch/test_task.py). CPU и отдельный сервер |
| [03. RRF и сравнение](tasks/03-comparison/README.md) | Объединить ранги и сравнить выдачи на одной разметке | [solution.py](tasks/03-comparison/solution.py) · [Тесты](tasks/03-comparison/test_task.py). CPU, функция без сервера |

```bash
make task TASK=14-elasticsearch-opensearch/01-elasticsearch
make task TASK=14-elasticsearch-opensearch/02-opensearch
make task TASK=14-elasticsearch-opensearch/03-comparison
```

До реализации функций ожидается `NotImplementedError`. Серверные проверки требуют явных флагов. Read-only probe читает заранее подготовленный `course-docs`. Проверка с записью вызывает твои функции в собственном UUID-индексе и удаляет только его. Точные команды, переменные адресов и требования находятся в README заданий. `make test` проверяет готовую обвязку курса.

## Остановка стенда

Останови использованный сервер:

```bash
docker compose -f labs/search/elasticsearch.compose.yaml down
docker compose -f labs/search/opensearch.compose.yaml down
deactivate
```

Обычный `down` сохраняет volumes. Корпус, qrels, mappings и исходные измерения нужны для восстановления и сравнения. `down -v` удаляет данные и для завершения заданий не требуется.

## Как работает текстовый поиск

**Индекс** хранит документы и структуры для быстрого поиска. **Анализатор** превращает текст в токены — единицы поиска. Например, при стандартной обработке слово `Vault` можно найти запросом `vault`. Это отличается от сравнения целой строки. **Инвертированный индекс** связывает токен со списком документов, где он встречается.

**BM25** ранжирует совпавшие документы: учитывает, насколько редок термин в корпусе, сколько раз он встречается в документе и какова длина документа. Это оценка совпадения текста, а не вероятность правильного ответа. Точный ID или имя настройки часто лучше искать лексически. Перефразировка «вернуть старую модель» может не совпасть со словом `rollback`. Векторный сигнал помогает там, где модель распознаёт близость смысла.

У `text` mapping типа `text`: содержимое анализируется. У `topic` тип `keyword`: значение сохраняется для точного фильтра, например `security`, без смыслового поиска. Backend-аналогия — полнотекстовый индекс рядом с обычным фильтром по категории. Граница аналогии: поисковый движок имеет собственный ranking и refresh, поэтому успешная запись не всегда немедленно видна поиску.

## Mapping и путь документа

**Mapping** — схема полей и способа их индексации. Она задаётся до загрузки. Файлы лежат в `labs/search/` и рядом с заданиями. Цепочка работы: `corpus.json → клиент bulk → mapping и индекс → match/kNN → IDs и scores → метрики по qrels`. Сервер строит поисковые структуры, клиент вычисляет метрики и RRF.

| Поле mapping | Elasticsearch | OpenSearch | Значение |
|---|---|---|---|
| `vector.type` | `dense_vector` | `knn_vector` | Векторное поле соответствующего движка |
| Размерность | `dims: 4` | `dimension: 4` | Четыре координаты ручного корпуса |
| Включение ANN | `index: true` | `settings.index.knn: true` | Подготовка индекса для приближённого поиска |
| Сходство | `similarity: cosine` | `space_type: cosinesimil` | Сравнение направлений |
| Метод OpenSearch | — | `hnsw`, `engine: lucene` | Графовый поиск и реализация, поддерживающая используемый фильтр |

Значение `vector` в JSON — имя поля, а не ключевое слово любого движка. Если переименовать поле, нужно согласованно изменить mapping, документы и запросы. При переходе к реальным embeddings меняется размерность: создаётся новый индекс и переиндексируется корпус. Старое поле нельзя исправить простой отправкой вектора другой длины.

## Bulk и два уровня ошибок

**Ingest** — загрузка документов. Bulk API уменьшает число сетевых запросов, объединяя операции в **NDJSON**: отдельный JSON на каждой строке. Для одного документа вход выглядит так:

```text
{"index":{"_index":"course-docs","_id":"7"}}
{"text":"Vault policies restrict secrets","topic":"security","vector":[0,0,0,1]}
```

После второй строки обязателен перевод строки. Это не JSON-массив. Первая строка задаёт действие, индекс и устойчивый `_id`, вторая — содержимое. Действие `index` с тем же `_id` заменяет документ, поэтому повторный импорт не увеличивает count. Пропавший из нового корпуса документ сам не удаляется. Используй `Content-Type: application/x-ndjson` и передачу файла через `--data-binary`, чтобы сохранить строки.

Ответ HTTP 200 говорит, что сервер обработал bulk-запрос. Внутри `items` отдельная операция может иметь `status:400` и `mapper_parsing_exception`, например из-за неверной размерности. Значит, нужно проверить каждый item: status >=300 либо поле error означают неуспех. Проверка только верхнего `errors` не даёт IDs для безопасного повторения. Это похоже на batch RPC с отдельным результатом каждой записи, а не на одну атомарную SQL-транзакцию.

Для видимости в учебной проверке после загрузки можно вызвать `POST /course-docs/_refresh` или использовать подходящий refresh-параметр bulk. Refresh делает изменения доступными поиску, но не исправляет ошибки items. Сначала разбирай запись, потом видимость.

## Два разных kNN-запроса

**kNN** — поиск k ближайших векторов. В Elasticsearch 8.17 учебный запрос отправляется в `/course-docs/_search`:

```json
{"knn":{"field":"vector","query_vector":[0,0,0,1],"k":2,"num_candidates":8},"size":2}
```

`field` выбирает поле, `query_vector` задаёт координаты, `k` — число соседей, `num_candidates` — число кандидатов ANN на shard, `size` — число возвращаемых hits. **Shard** — часть индекса, обрабатываемая отдельным поисковым исполнителем. Для маленького стенда распределение не является целью. `num_candidates=8` — настройка учебного запроса, а не обещание точного поиска для любого корпуса. Формат описан в [документации 8.17](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/knn-search.html).

В OpenSearch 2.19 для того же поля и Lucene engine:

```json
{"size":2,"query":{"knn":{"vector":{"vector":[0,0,0,1],"k":2,"filter":{"term":{"topic":"security"}}}}}}
```

Первый `vector` после `knn` — имя поля, второй — координаты. `filter` находится внутри объекта запроса к этому полю. Так поиск учитывает topic при выборе подходящих соседей. `post_filter` после малого top-k способен оставить меньше результатов. Поддержка этого фильтра зависит от engine: учебный mapping выбирает Lucene. См. [kNN query 2.19](https://docs.opensearch.org/2.19/query-dsl/specialized/k-nn/).

В обоих движках ожидается набор IDs `7,8` для security-вектора. В HTTP hits `_id` является строкой. Для лексического запроса `{"query":{"match":{"text":"Vault"}}}` среди hits должен быть ID `7`. Значения `_score` не обязаны совпадать между движками: по ним нельзя проверять численную эквивалентность разных систем.

## Гибридное ранжирование через RRF

**Hybrid search** объединяет несколько сигналов. Сумма BM25 score=8 и cosine=0.9 не имеет ясного смысла: шкалы различаются. **Reciprocal rank fusion (RRF)** использует только позиции. Для документа складываются `1/(c+rank)` из списков, где он найден. Rank начинается с 1, здесь c=60. Это клиентская операция над IDs. Специальная платная серверная функция не требуется.

Пусть lexical=`[1,2]`, vector=`[2,3]`. Тогда ID1: `1/61≈0.01639`, ID2: `1/62+1/61≈0.03252`, ID3: `1/62≈0.01613`. Итог `[2,1,3]`: документ 2 получает подтверждение от двух источников. Это демонстрация правила, а не доказательство, что документ 2 релевантен.

В упражнении повтор ID в одном списке учитывается только на первой позиции, но позиции остальных не сдвигаются: для `[1,1,2]` ID2 сохраняет rank=3. При равной сумме сохраняется порядок первого появления в исходных списках. Такая детерминированность нужна, чтобы одинаковый вход давал одинаковый результат.

**Candidate pool** — набор документов, доступных для итогового ранжирования. Если lexical берёт 5 кандидатов, а vector 100, результат зависит также от объёма отбора. Фиксируй глубину исходных выдач и конечный k. Сравни lexical/vector/RRF по тем же qrels, Recall@2 и среднему reciprocal rank. Определения — в [модуле 13](../13-qdrant/README.md#качество-выдачи-и-разобранные-метрики).

## Ресурсы и диагностика стенда

Compose использует `discovery.type: single-node`: сервер работает без поиска других узлов. Heap JVM задан `-Xms768m -Xmx768m`, но контейнеру разрешено 2g. Heap — память управляемых Java-объектов. Кроме неё нужны native memory и файловый cache. Поэтому Xmx не является пределом всей памяти процесса.

Security в учебных конфигурациях отключена, порты связаны с `127.0.0.1`. Это локальная среда, а не готовая схема доступа нескольких команд. `vm.max_map_count` — лимит Linux memory mappings. При ошибке bootstrap проверяй logs и настройку Linux runtime, в котором работает Docker. Изменение настройки внешней ОС не обязательно меняет VM Docker.

| Симптом | Что проверять |
|---|---|
| `connection refused` | Контейнер, logs и опубликованный порт. Это ещё не ошибка mapping |
| Не удаётся занять 9200 | Не остановлен другой поисковый Compose-стенд |
| bulk HTTP 200, count меньше 8 | Ошибки items, устойчивость IDs, затем refresh |
| Ошибка неизвестного поля запроса | Соответствие JSON конкретному движку и pinned версии |
| Неверная dimension | Mapping и фактический encoder. Retry не изменит схему |
| Контейнер завершён по памяти | Лимит контейнера, heap и остальные одновременно работающие стенды |

Восемь документов проверяют интерфейс, но не масштабирование. Для измерений сохраняй corpus/qrels hashes, параметры поиска, исходные задержки, число запросов, warmup и ресурсы. Разделяй ingest time, latency одного поиска и throughput нагрузки. Остановка `down` сохраняет volumes. Перед их удалением оставь исходный корпус и настройки восстановления.

## Материалы

- [Elasticsearch bulk 8.17](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/docs-bulk.html) — формат строк, refresh и ошибки операций.
- [Elasticsearch kNN 8.17](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/knn-search.html) — candidate search и схема запроса.
- [OpenSearch kNN 2.19](https://docs.opensearch.org/2.19/query-dsl/specialized/k-nn/) — фильтры и параметры поддерживаемых engines.
- [OpenSearch Docker 2.19](https://docs.opensearch.org/docs/2.19/install-and-configure/install-opensearch/docker/) — memory и Linux prerequisites.

## SDK как граница приложения

Для Elasticsearch 8.17.3 используется Python client 8.17.2, для OpenSearch 2.19.1 — opensearch-py 2.8.0 (`labs/search/requirements.txt`). Их top-level импорты находятся в заготовках. Отсутствие пакета допускается при сборе чистых тестов, сетевые команды требуют установленного SDK. Клиент управляет транспортом, а твой код отвечает за mapping, сохранение IDs, разбор каждого bulk item, refresh и преобразование hits.

Реальный путь практики: CLI → ensure_index → build_bulk/client.bulk/bulk_failures → refresh → lexical_search/vector_search → нормализованные IDs/score/payload → ranking_metrics и RRF. Функции SDK оставлены студенту как NotImplementedError. CLI уже разбирает параметры, создаёт клиент и закрывает его. Read-only probe проверяет готовый course-docs. Отдельные integration/writes тесты под двумя флагами MLOPS_RUN_INTEGRATION=1 и MLOPS_RUN_WRITES=1 вызывают студенческий ingest/query в уникальном имени и удаляют только это имя. Команды и точные контракты — в заданиях.

# OpenSearch: собственный kNN-запрос

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## С чего начать

Реализуй `knn_request(vector, k, topic=None, dimension=4) -> dict`. Схема: size=k, query.knn.vector={vector, k}; при topic добавь filter.term.topic внутрь этого объекта. k — положительное целое; dimension должна совпадать, вектор конечный и ненулевой. Это shape OpenSearch с Lucene engine, не JSON Elasticsearch. Mapping лежит рядом; реальные запросы используй на том же корпусе и embeddings.

Подготовь [основное окружение](../../../../SETUP.md). Все команды ниже выполняются из корня курса. Платформа задания: **cpu**. Функции и ожидаемые результаты описаны также в `test_task.py`; тесты используют небольшие фиксированные данные.

## Исходное задание

```bash
docker compose -f labs/search/elasticsearch.compose.yaml down
docker compose -f labs/search/opensearch.compose.yaml up -d
curl -sS -X PUT http://localhost:9200/course-docs -H 'Content-Type: application/json' --data-binary @labs/search/opensearch.mapping.json
```

Реализуй отдельный request shape для OpenSearch. Повтори тот же корпус, queries и k. Ошибки запуска сначала диагностируй по logs; для vm.max_map_count следуй инструкции своего Linux runtime.

## Проверка

```bash
make task TASK=14-elasticsearch-opensearch/02-opensearch
```

У этой задачи проверяются функции: запускай их тестами, отдельного CLI нет.

До реализации функции ожидается `NotImplementedError`. Реализуй заготовку, сохраняя контракт функций из тестов. Офлайн-тест не подтверждает действия на внешнем стенде: проверки, требующие работающего сервиса, включаются явно через `MLOPS_RUN_INTEGRATION=1`.

## Результат

Функции должны проходить проверки положительных и отрицательных случаев. Для собственного эксперимента сохраняй исходные измерения в `work/`: они пригодятся для повторного сравнения. Отдельное письменное резюме не требуется. После работы останови стенд по инструкции practice.md.

### Реальная проверка запроса на OpenSearch

```bash
MLOPS_RUN_INTEGRATION=1 OPENSEARCH_URL=http://127.0.0.1:9200 make task TASK=14-elasticsearch-opensearch/02-opensearch
```

Probe отправляет результат твоей функции `knn_request` уже подготовленному OpenSearch. Ожидаемые инварианты общего корпуса: count=8, отфильтрованные kNN IDs 7/8 с topic=security, документ 7 в match по Vault. Это не замер производительности. Probe только читает; индекс и mapping подготовь отдельно. Без opt-in пропуск, при включении отсутствие URL, сервера или индекса — ошибка.

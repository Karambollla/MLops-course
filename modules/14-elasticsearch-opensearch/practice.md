# Практика: Elasticsearch и OpenSearch: сравнение поиска

[Теория](README.md) · [Подсказки](hints.md)

## Подготовка

Останови Qdrant, ClearML и другие тяжёлые стенды. Запускай только один движок на порту 9200.

```bash
docker compose -f labs/search/elasticsearch.compose.yaml up -d
curl -sS http://localhost:9200
curl -sS -X PUT http://localhost:9200/course-docs -H 'Content-Type: application/json' --data-binary @labs/search/elasticsearch.mapping.json
```

## Задание 1. Elasticsearch

Напиши ingest-скрипт из corpus.json: стабильные IDs, NDJSON bulk, проверка items. Реализуй match-запрос и knn-запрос для одного query vector. Сохрани top-5, scores и время. Повторный ingest не меняет число документов.

## Задание 2. OpenSearch

```bash
docker compose -f labs/search/elasticsearch.compose.yaml down
docker compose -f labs/search/opensearch.compose.yaml up -d
curl -sS -X PUT http://localhost:9200/course-docs -H 'Content-Type: application/json' --data-binary @labs/search/opensearch.mapping.json
```

Реализуй отдельный request shape для OpenSearch. Повтори тот же корпус, queries и k. Ошибки запуска сначала диагностируй по logs; для vm.max_map_count следуй инструкции своего Linux runtime.

## Задание 3. Сравнение

Сделай client-side RRF с c=60. Сравни keyword/vector/hybrid по Recall@2 и MRR на одинаковых qrels. Затем повтори на настоящих embeddings из модуля 13 с новой размерностью индексов. Не считай toy-векторы результатом обучения модели.

## Критерии готовности

- [ ] Оба движка реально проверены либо недоступный запуск честно отмечен.
- [ ] Нет ошибок bulk items, IDs устойчивы.
- [ ] Сравнение использует одинаковый corpus, embeddings, qrels и candidate pool.
- [ ] Есть объяснение различий mappings, scores и ресурсного бюджета.

## Завершение

Останови активный compose-стенд командой down. Перед удалением его volumes сохрани mappings, корпус, qrels и отчёт. Не запускай оба на одном host port.

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

До реализации функции ожидается `NotImplementedError`; для отчётов — ошибка незаполненного поля. Исправляй заготовку или собственный результат, сохраняя ожидаемое поведение тестов. Офлайн-тест не подтверждает действия на внешнем стенде: проверки, требующие работающего сервиса, включаются явно через `MLOPS_RUN_INTEGRATION=1`.

## Критерии и завершение

Покажи результаты исходного задания и объясни позитивные и негативные случаи из тестов. Сохрани собственные измерения и команды в work/. Затем останови стенд по общей инструкции practice.md модуля.

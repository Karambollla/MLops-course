# Практика: Elasticsearch и OpenSearch: сравнение поиска

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Elasticsearch: bulk и ошибки](tasks/01-elasticsearch/README.md) | [Заготовка](tasks/01-elasticsearch/solution.py) · [тесты](tasks/01-elasticsearch/test_task.py) | cpu |
| [OpenSearch: собственный kNN-запрос](tasks/02-opensearch/README.md) | [Заготовка](tasks/02-opensearch/solution.py) · [тесты](tasks/02-opensearch/test_task.py) | cpu |
| [Сравнение и RRF](tasks/03-comparison/README.md) | [Заготовка](tasks/03-comparison/solution.py) · [тесты](tasks/03-comparison/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=14-elasticsearch-opensearch/01-elasticsearch
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

Останови Qdrant, ClearML и другие тяжёлые стенды. Запускай только один движок на порту 9200.

```bash
docker compose -f labs/search/elasticsearch.compose.yaml up -d
curl -sS http://localhost:9200
curl -sS -X PUT http://localhost:9200/course-docs -H 'Content-Type: application/json' --data-binary @labs/search/elasticsearch.mapping.json
```

## Завершение

Останови активный compose-стенд командой down. Перед удалением его volumes сохрани mappings, корпус, qrels и отчёт. Не запускай оба на одном host port.

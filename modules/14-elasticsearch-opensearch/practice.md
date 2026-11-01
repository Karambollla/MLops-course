# Практика: Elasticsearch и OpenSearch: сравнение поиска

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Elasticsearch: bulk и ошибки](tasks/01-elasticsearch/README.md) | [Старт](tasks/01-elasticsearch/solution.py) · [Проверка стенда](tasks/01-elasticsearch/test_task.py) | cpu |
| [OpenSearch: собственный kNN-запрос](tasks/02-opensearch/README.md) | [Старт](tasks/02-opensearch/solution.py) · [Проверка стенда](tasks/02-opensearch/test_task.py) | cpu |
| [Сравнение и RRF](tasks/03-comparison/README.md) | [Старт](tasks/03-comparison/solution.py) · [Тесты функций](tasks/03-comparison/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=14-elasticsearch-opensearch/01-elasticsearch
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Тесты проверяют функции и наблюдаемое поведение. Текстовый отчёт для прохождения не требуется.

## Подготовка

Останови Qdrant, ClearML и другие тяжёлые стенды. Запускай только один движок на порту 9200.

```bash
docker compose -f labs/search/elasticsearch.compose.yaml up -d
curl -sS http://localhost:9200
curl -sS -X PUT http://localhost:9200/course-docs -H 'Content-Type: application/json' --data-binary @labs/search/elasticsearch.mapping.json
```

## Завершение

Останови активный compose-стенд командой down. Перед удалением его volumes сохрани mappings, корпус, qrels и исходные измерения. Не запускай оба на одном host port.

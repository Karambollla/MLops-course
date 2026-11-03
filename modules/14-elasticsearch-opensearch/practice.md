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
python -m pip install -r labs/search/requirements.txt
python modules/14-elasticsearch-opensearch/tasks/01-elasticsearch/solution.py index --index course-docs
```

После реализации SDK-заготовок CLI делает создание/проверку mapping, bulk с проверкой каждого item, refresh и поиск. Повторный ingest сохраняет 8 документов, Vault находит ID7, security kNN — 7/8. Функции поиска возвращают IDs, score и payload; их IDs поступают в ranking_metrics/RRF. Нужны также завершённые 13/02-evaluation и 14/03-comparison.

```bash
# Только тесты, создающие собственный UUID-индекс и удаляющие его в finally:
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 ELASTICSEARCH_URL=http://127.0.0.1:9200 python scripts/run_task.py test 14-elasticsearch-opensearch/01-elasticsearch -- -m writes
# Для OpenSearch: OPENSEARCH_URL и задача 02-opensearch, после остановки ES.
```

Без обоих флагов writes пропускаются. `MLOPS_RUN_INTEGRATION=1` отдельно включает прежние read-only probes по заранее подготовленному course-docs; ограничивай запуск `-m 'integration and not writes'`, если нужен только probe. Проверка функции и probe не заменяют вызов SDK-загрузки и поиска твоим кодом.

## Завершение

Останови активный compose-стенд командой down. Перед удалением его volumes сохрани mappings, корпус, qrels и исходные измерения. Не запускай оба на одном host port.

# Практика: Qdrant и основы векторного поиска

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Qdrant: загрузка и фильтрация](tasks/01-plumbing/README.md) | [Заготовка](tasks/01-plumbing/solution.py) · [тесты](tasks/01-plumbing/test_task.py) | cpu |
| [Recall, precision и MRR](tasks/02-evaluation/README.md) | [Заготовка](tasks/02-evaluation/solution.py) · [тесты](tasks/02-evaluation/test_task.py) | cpu |
| [Версия настоящих embeddings](tasks/03-embeddings/README.md) | [Заготовка](tasks/03-embeddings/solution.py) · [тесты](tasks/03-embeddings/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=13-qdrant/01-plumbing
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

## Подготовка

В отдельном Python 3.12 окружении установи `labs/qdrant/requirements.txt`.

```bash
docker compose -f labs/qdrant/compose.yaml up -d
curl -sS http://localhost:6333/collections
```

## Завершение

`docker compose -f labs/qdrant/compose.yaml down` сохраняет данные. До `down -v` сохрани corpus, qrels, model metadata и результаты.

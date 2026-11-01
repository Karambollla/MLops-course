# Практика: Qdrant и основы векторного поиска

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Qdrant: загрузка и фильтрация](tasks/01-plumbing/README.md) | [Старт](tasks/01-plumbing/solution.py) · [Проверка стенда](tasks/01-plumbing/test_task.py) | cpu |
| [Recall, precision и MRR](tasks/02-evaluation/README.md) | [Старт](tasks/02-evaluation/solution.py) · [Тесты функций](tasks/02-evaluation/test_task.py) | cpu |
| [Версия настоящих embeddings](tasks/03-embeddings/README.md) | [Старт](tasks/03-embeddings/solution.py) · [Тесты функций](tasks/03-embeddings/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=13-qdrant/01-plumbing
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Тесты проверяют функции и наблюдаемое поведение. Текстовый отчёт для прохождения не требуется.

## Подготовка

В отдельном Python 3.12 окружении установи `labs/qdrant/requirements.txt`.

```bash
docker compose -f labs/qdrant/compose.yaml up -d
curl -sS http://localhost:6333/collections
```

## Завершение

`docker compose -f labs/qdrant/compose.yaml down` сохраняет данные. До `down -v` сохрани corpus, qrels, model metadata и результаты.

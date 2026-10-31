# Практика: Qdrant и основы векторного поиска

[Теория](README.md) · [Подсказки](hints.md)

## Подготовка

В отдельном Python 3.12 окружении установи `labs/qdrant/requirements.txt`.

```bash
docker compose -f labs/qdrant/compose.yaml up -d
curl -sS http://localhost:6333/collections
```

## Задание 1. Plumbing

Реализуй `labs/qdrant/search.py`: коллекция `course-docs`, размерность 4, cosine, устойчивые integer IDs. Загрузи корпус и выполни запросы из `labs/search/queries.json` через `query_points`. Повторная загрузка сохраняет ровно 8 points. Проверь фильтр topic=security и ошибку неверной размерности.

## Задание 2. Оценка

Реализуй Recall@2 и MRR. Для ручных векторов ожидается Recall@2=1 на четырёх учебных запросах; это проверка wiring, а не доказательство семантического качества. Отдельно проверь метрику на выдаче [1,3] при relevant [1,2]: Recall@2=0,5.

## Задание 3. Настоящие embeddings

В том же отдельном окружении установи `fastembed==0.6.1`. Выбери `BAAI/bge-small-en-v1.5`, зафиксируй model ID и revision/cache snapshot. Сгенерируй embeddings корпуса и запросов на CPU, определи размерность по фактическому выходу и создай новую коллекцию. Затем расширь собственный корпус до 30 документов и разметь 20 запросов. Сравни keyword baseline и vector search по одним qrels, не меняя разметку ради результата.

## Критерии готовности

- [ ] Upsert не дублирует документы, фильтр и размерность проверены.
- [ ] Метрика проверена на известном примере, отчёт содержит per-query результаты.
- [ ] Ручные векторы и настоящие embeddings явно разделены.
- [ ] После restart коллекция доступна; описан способ восстановления.

## Завершение

`docker compose -f labs/qdrant/compose.yaml down` сохраняет данные. До `down -v` сохрани corpus, qrels, model metadata и результаты.

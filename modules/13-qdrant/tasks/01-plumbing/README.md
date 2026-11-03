# Qdrant: загрузка и фильтрация

[Теория](../../README.md) · [Практика модуля](../../practice.md) · [Подсказки](../../hints.md)

## Зачем нужна загрузка с устойчивыми IDs

Поисковый сервис должен получать те же документы после повторного импорта, а не новую копию каждого. Здесь ты соединяешь JSON-корпус с Qdrant и проверяешь фильтрацию по теме. Как устроены point, payload и upsert, объясняется в [пути данных](../../README.md#коллекция-и-путь-данных), а место фильтра — в [разборе запроса](../../README.md#запрос-и-фильтрация).

Уже предоставлены `labs/search/corpus.json` с восемью ручными 4D-векторами, `queries.json`, Compose Qdrant 1.13.6 и заготовка `solution.py`. Нужны [основное окружение](../../../../SETUP.md), отдельные зависимости `labs/qdrant/requirements.txt` и локальный CPU-стенд. Языковая embedding-модель не нужна.

## Что реализовать

В `solution.py` заполни функции, сохранив сигнатуры:

- `build_points(documents) -> list[dict]` преобразует документы в записи `{id, vector, payload:{text,topic}}`. IDs — уникальные неотрицательные integer без bool; vector — конечные числа одинаковой непустой размерности и не нулевой целиком. Повтор ID, неверный ID, NaN/infinity, нулевой вектор или разные размерности вызывают ValueError.
- `index_documents(url, corpus_path, collection="course-docs") -> None` читает JSON, создаёт/использует коллекцию `course-docs` с размерностью 4 и cosine и выполняет настоящий upsert. Повторная загрузка исходного корпуса сохраняет ровно восемь points. При несовместимой существующей схеме выброси ValueError, сохранив её данные. Имя collection позволяет изолировать эксперименты; старый вызов из двух аргументов сохраняется.

- `query_documents(url,vector,k=2,topic=None,collection="course-docs",dimension=4) -> list[dict]` создаёт клиент, вызывает `query_points(...,with_payload=True)` и разбирает `.points`. Результат в порядке Qdrant: `{id:int,score:float,payload:{text,topic}}`. topic задаёт Filter/FieldCondition/MatchValue в query_filter. Пустые hits — []. Неверные k/dimension (положительные целые без bool), размерность, NaN/infinity или нулевая норма — ValueError до SDK. Закрой созданный клиент.

CLI main уже разбирает `--url`, `--corpus`, `--collection`, `--action index|query`, `--vector`, `--k`, `--topic`, `--dimension`; прежний запуск без --action выполняет index. Импорты `QdrantClient` и `models` уже подготовлены в начале модуля. Обработка отсутствия SDK позволяет проверять чистые функции отдельно от подключения.

Для отдельного документа `{"id":7,"text":"Vault policy","topic":"security","vector":[0,1]}` корректное преобразование — `{"id":7,"vector":[0,1],"payload":{"text":"Vault policy","topic":"security"}}`. Этот 2D-пример проверяет общую функцию; серверная коллекция корпуса остаётся 4D.

## Запуск и проверка взаимодействия

Все команды из корня курса:

```bash
docker compose -f labs/qdrant/compose.yaml up -d
curl --fail http://127.0.0.1:6333/collections
python -m pip install -r labs/qdrant/requirements.txt
python modules/13-qdrant/tasks/01-plumbing/solution.py --url http://127.0.0.1:6333 --corpus labs/search/corpus.json
python modules/13-qdrant/tasks/01-plumbing/solution.py --action query --vector 0 0 0 1 --topic security
make task TASK=13-qdrant/01-plumbing
```

Запуск Python требует реализованной функции: исходная заготовка завершится NotImplementedError. Выполни CLI повторно, проверь count=8 и запросы через `query_points(...).points`. Для security-вектора `[0,0,0,1]` top-2 содержит IDs 7/8. Фильтр topic=security также возвращает только эти IDs. Вектор `[1,0]` не соответствует схеме: query_documents должен отклонить его ValueError до SDK. При прямом HTTP-запросе сервер отвечает 400, что отдельно проверяет read-only probe. Геометрия этого примера разобрана в [теории](../../README.md#от-текста-к-embedding-и-расстоянию).

Явно включаемая проверка читает уже подготовленную коллекцию и отправляет поисковые запросы:

```bash
MLOPS_RUN_INTEGRATION=1 QDRANT_URL=http://127.0.0.1:6333 python scripts/run_task.py test 13-qdrant/01-plumbing -- -m 'integration and not writes'
```

Она не создаёт и не удаляет коллекцию. Без opt-in серверная проверка пропущена, unit-тесты преобразования выполняются. При opt-in недоступный сервер или неверный корпус приводят к ошибке. Набор 7/8 — ожидаемый инвариант, а не измеренный здесь результат качества модели.

## Завершение

Сохрани корпус и необходимые конфигурации, останови `docker compose -f labs/qdrant/compose.yaml down`. Volume останется; `down -v` удалит данные и не нужен для этого задания. Отдельный текстовый отчёт не требуется.

## Локальная проверка SDK

После реализации задания и его предшественников можно проверить Qdrant в памяти процесса. Установи зависимости модуля в его окружение, затем выполни из корня курса:

```bash
MLOPS_RUN_SDK=1 python scripts/run_task.py test 13-qdrant/01-plumbing -- -m sdk
```

Используются только временные данные, внешний сервер не нужен. Без флага проверка пропускается; при включённом флаге отсутствие SDK считается ошибкой подготовки окружения. Этот запуск не заменяет практику работающего стенда. Подробнее — [режимы проверок](../../../../docs/task-structure.md#локальные-проверки-sdk).

## Проверка своего загрузчика и поиска на сервере

Сначала реализуй также ranking_metrics в 13/02-evaluation. Затем включи отдельный записывающий тест:

```bash
MLOPS_RUN_INTEGRATION=1 MLOPS_RUN_WRITES=1 QDRANT_URL=http://127.0.0.1:6333 python scripts/run_task.py test 13-qdrant/01-plumbing -- -m writes
```

Тест отмечен integration/writes, проверяет отсутствие нового UUID-имени, дважды вызывает твою index_documents для этого имени и вызывает твою query_documents по всем четырём queries. Реальные IDs сравниваются с независимыми qrels через твою ranking_metrics; на ручном корпусе ожидаются recall=precision=mrr=1 при k=2. Дополнительно проверяются security filter и пустой неизвестный topic. finally удаляет только созданное тестовое имя. Без обоих флагов тест пропущен; при включении отсутствие SDK, сервера или реализации — ошибка.

Локальный sdk-тест тоже вызывает query_documents, включая named collection и фильтрацию. Проверка исходного course-docs прямым HTTP остаётся read-only диагностикой. Она не доказывает выполнение твоей SDK-реализации. Доступность endpoint и качество настоящей embedding-модели этими инструкциями не заявляются.

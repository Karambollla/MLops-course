# Версия настоящих embeddings

[Модуль и подготовка](../../README.md#подготовка-к-заданиям) · [Все задания модуля](../../README.md#задания) · [Окружение курса](../../../../SETUP.md)

## Зачем менять ручные векторы

Восемь условных векторов подтверждают правильность API, но не показывают, умеет ли поиск понимать перефразировки. Теперь векторы вычисляет настоящая модель, а манифест связывает индекс с её версией и корпусом. Причина согласованной смены модели запросов и документов — в [теории embeddings](../../README.md#от-текста-к-embedding-и-расстоянию), состав версии — в [разделе индекса](../../README.md#настоящие-embeddings-и-версия-индекса).

Уже есть CPU-окружение Qdrant, корпус и функция метрик из предыдущих заданий. В соседнем [solution.py](solution.py) реализуй `make_manifest`. Для вызовов encoder и создания нового индекса используй отдельный локальный Python-фрагмент. Модель и новый индекс эта функция не скачивает и не создаёт. Нужны [основное окружение](../../../../SETUP.md) и отдельное окружение для encoder.

## Шаг 1. Связать векторы с исходными данными

```python
def make_manifest(model_id: str, revision: str, vectors: list[list[float]], corpus_bytes: bytes) -> dict:
    ...
```

| Параметр | Тип | Формат и смысл | Откуда взять | Пример |
|---|---|---|---|---|
| `model_id` | `str` | Идентификатор модели, вычислившей vectors | Конфигурация CPU encoder | `"BAAI/bge-small-en-v1.5"` |
| `revision` | `str` | Идентификатор фактически использованного неизменяемого snapshot | Metadata скачанной модели/cache, а не предположение по имени | `"a" * 40` в тесте |
| `vectors` | `list[list[float]]` | По одному непустому вектору одинаковой размерности на документ | Результат CPU encoder, преобразованный в списки | `[[1,0],[0,1]]` |
| `corpus_bytes` | `bytes` | Исходные байты файла до JSON-декодирования и изменения пробелов | `Path("labs/search/corpus.json").read_bytes()` | `b"corpus"` в тесте |

Форма результата: `{"model_id":"...","revision":"...","dimension":2,"count":2,"corpus_sha256":"..."}`. SHA-256 — строка из 64 шестнадцатеричных символов. Пример revision обозначает формат тестового входа и не является настоящей версией весов.

## Контракт манифеста

Реализуй `make_manifest(model_id, revision, vectors, corpus_bytes) -> dict` с ровно полями `model_id`, `revision`, `dimension`, `count`, `corpus_sha256`. Dimension определяется по фактическому вектору, count — по числу векторов, SHA-256 — по исходным bytes корпуса. Сохраняй bytes до декодирования/переформатирования: одинаковые документы в JSON с другими пробелами имеют другой hash.

Векторы должны быть непустыми, конечными, ненулевыми и одинаковой размерности. Пустой набор и неверная геометрия — ValueError. Revision описывает неизменяемый snapshot. `main` и `latest` отклоняются как изменяемые ссылки. Само записанное поле не гарантирует, что encoder действительно загрузил эти веса.

Для двух векторов `[[1,0],[0,1]]` правильные dimension=2 и count=2, независимо от имени модели. При входе `corpus_bytes=b"corpus"` hash должен совпасть с `hashlib.sha256(b"corpus").hexdigest()`. Такой маленький пример проверяет происхождение данных, а не смысл embedding.

## Шаг 2. Получить CPU-векторы и создать отдельную коллекцию

В окружении Qdrant установи `fastembed==0.6.1`. После этого маленький фрагмент показывает границу SDK: входом остаются тексты исходного корпуса, выходом становятся новые массивы вместо ручного поля `vector`.

```python
import json
from pathlib import Path
from fastembed import TextEmbedding
from huggingface_hub import model_info, snapshot_download

corpus_bytes = Path("labs/search/corpus.json").read_bytes()
documents = json.loads(corpus_bytes)
source = "qdrant/bge-small-en-v1.5-onnx-q"
revision = model_info(source).sha
model_dir = snapshot_download(source, revision=revision, cache_dir="work/fastembed-cache")
encoder = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    specific_model_path=model_dir,
    providers=["CPUExecutionProvider"],
)
vectors = [vector.tolist() for vector in encoder.embed([doc["text"] for doc in documents])]
```

`model_info(source).sha` получает commit ONNX-источника, `snapshot_download` скачивает именно его в `cache_dir`. Сохрани полученный `revision`: при повторении используй сохранённое значение вместо нового разрешения текущего commit. `specific_model_path` передаёт этот каталог encoder, `model_name` выбирает способ обработки, `providers` — CPU. Эти аргументы поддерживает [FastEmbed 0.6.1](https://github.com/qdrant/fastembed/blob/v0.6.1/fastembed/text/onnx_embedding.py). `huggingface_hub` устанавливается как его зависимость. `embed` возвращает по массиву на документ. Список сохраняет порядок связи с IDs.

Имени `BAAI/bge-small-en-v1.5` в этой версии соответствует ONNX-репозиторий `qdrant/bge-small-en-v1.5-onnx-q`. Поэтому в `make_manifest` передай выбранный model ID и `revision` из фрагмента, а источник и локальные файлы сохрани рядом. SHA upstream-репозитория BAAI не описывает этот ONNX snapshot.

Для запросов используй тот же encoder и выбранную подготовку текста. Прочитай [model card](https://huggingface.co/BAAI/bge-small-en-v1.5): если используешь query instruction, добавляй её к запросам согласованно во всех сравнениях и сохраняй эту настройку. Манифест принимает уже полученные vectors и bytes. Его чистая проверка не требует скачивания модели.

Получай embeddings корпуса и запросов на CPU. Проверь число выходных векторов и размерность, создай новую коллекцию с этой размерностью. Не переписывай ручную `course-docs`, нужную probe первого задания. Для проверки качества расширь собственную копию корпуса до 30 документов и независимо разметь 20 запросов. Сравни keyword baseline и vector search по одинаковым qrels и k. Отдели подбор параметров от финальной проверки.

Корректное взаимодействие: одна revision encoder → N документов и N векторов размерности D → коллекция с size=D → запрос encoder той же версии → top-k IDs → метрики по отдельной разметке. Успешный count не доказывает качество. Несовпадающие model revisions могут дать плохой ranking без HTTP-ошибки.

## Шаг 3. Проверить манифест и оценить поиск

```bash
make task TASK=13-qdrant/03-embeddings
```

Тесты вызывают только `make_manifest`, CLI нет. До реализации ожидается NotImplementedError. Эти тесты не запускают FastEmbed и не подтверждают качество языковой модели. Сохрани corpus/qrels, metadata, snapshot и исходные выдачи в `work/` для повторения. Останови Qdrant через `docker compose -f labs/qdrant/compose.yaml down`, сохранив volume.

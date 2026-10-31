# Проверка подготовки курса

Дата проверки: **2026-10-31**. Среда: macOS ARM64, Apple M5, 16 ГБ RAM. Проверки Python выполнены в изолированных временных окружениях с CPython **3.12.12**. Системный Python 3.14 не изменялся.

## Дополнительная проверка после восстановления Docker

CPU Docker-проверки выполнены: **9 Compose-стендов, Terraform apply/plan/drift/destroy и kind/Helm rollout/rollback**. Найденные проблемы исправлены. Полные результаты, границы и команды — в [Docker-отчёте](docker-verification.md), машинные статусы — в [JSON](docker-checks.json).

Таблица ниже сохраняет результаты первоначальной подготовки; прежние ограничения Docker сняты для перечисленных в новом отчёте CPU-стендов.

## Первоначальные подтверждённые результаты

| Проверка | Результат | Граница проверки |
|---|---|---|
| `make check` | 18 модулей, все внутренние ссылки, fences, UTF-8, Python AST и JSON корректны | Проверяет материалы и синтаксис, не решает упражнения |
| Markdownlint CLI2 0.18.1 | 0 ошибок | Длина строки не ограничивается, остальные стандартные правила включены |
| Внешние источники | 66 уникальных ссылок авторских материалов ответили успешно | HTTP GET с redirects; доступность не гарантируется навсегда |
| Готовая HTTP-обвязка | 6 тестов прошли, 2 учебных пропущены явно | Проверены 200/422/503, метрики, настоящий toy bundle, порядок признаков и отказ на неверный bundle |
| Учебные тесты с RUN_EXERCISES=1 | Два ожидаемых падения NotImplementedError | Подтверждает, что задания не заменены готовыми решениями |
| California Housing | 20640 строк, 9 столбцов, SHA-256 сохранена | Загрузчик выполнен с выходом во временную папку; модель учащегося не обучалась |
| Compose | 13 конфигураций проходят `config --quiet` | Не проверяет runtime, существование модели и доступность daemon |
| YAML | 22 исходных файла и Helm render разобраны | Не заменяет Kubernetes server-side validation |
| Image tags | 18 используемых tags существуют по registry metadata | Manifests не доказывают запуск и совместимость GPU; single manifest может не перечислять платформы |
| Helm 3.17.3 | Lint и template проходят | Релиз в реальном кластере не устанавливался; icon необязателен |
| Terraform 1.11.4 | Init, fmt-check и validate проходят; provider 3.0.2 | Apply/plan с Docker не выполнены; lock provider сохранён; validate требует разрешённого IPC вне sandbox |
| Ansible 2.18.4 | Syntax-check; временный локальный запуск: changed=2, затем changed=0 | Путь вывода заменён на /tmp; Docker/Linux и SSH не проверены |
| MLflow 3.1.1 | Нативный HTTP server, SQLite, artifact roundtrip, sklearn registry и alias | Тестовая toy-модель; не контейнер и не решение housing |
| ONNX CPU | Toy Pipeline экспортирован, parity проходит с rtol=1e-4/atol=1e-5 | Не заменяет экспорт собственного Pipeline учащегося |
| Qdrant client | In-memory upsert, повтор без дубликатов, filter, query_points, toy Recall@2=1 | Не Docker Server и не оценка настоящих semantic embeddings |
| Зависимости | Основной lock установлен; ClearML SDK/Agent, Qdrant/FastEmbed, ONNX и DVC разрешаются отдельно | Resolution не равен запуску всех библиотек и моделей |
| Bash | `bash -n labs/llm/tensorrt-llm.sh` проходит | Не запускает NVIDIA container |

## Исправления по результатам проверки

- Закреплены packaging 25.0 и SQLAlchemy 2.0.41: новые транзитивные версии были несовместимы с выбранным MLflow. После исправления нативный сервер и registry проверены.
- SDK и Agent ClearML разделены: ограничения six у Agent отличаются от окружения обучения.
- Образ SGLang заменён на существующий `v0.4.10.post2-cu126`.
- Ошибка сериализации NaN/Infinity в ответе валидации исправлена через безопасный JSON без повторения сырого входа; regression test сначала воспроизвёл 500, затем получил 422.
- По [независимому обзору](review.md) исправлены исключения cache-каталогов, запуск Airflow и переход ClearML в online.

## Непроверенные сценарии

Docker daemon восстановлен, доступ подтверждён вне sandbox. Ранее непроверенные CPU-стенды из нового отчёта теперь проверены в реальных контейнерах. Дополнительные Linux x86_64-маршруты ClearML Server/Agent и Triton не запускались через эмуляцию.

NVIDIA GPU отсутствует: TensorRT-LLM, vLLM и SGLang не запускались. Реальных GPU TTFT, tokens/s и VRAM-сравнений нет. GitHub Actions не публиковался и в удалённом CI не запускался.

## Повторение проверок

После установки основного окружения:

```bash
make check
make test
make exercises
```

`make exercises` ожидаемо красный до реализации. Для форматирования при наличии Node:

```bash
npm exec --yes --package markdownlint-cli2@0.18.1 -- markdownlint-cli2 '**/*.md'
```

Сетевые источники: `make links`. Для каждого Compose-файла отдельно выполни `docker compose -f ПУТЬ config --quiet`. После запуска Docker повтори runtime-проверки по практике модулей и дополни собственный отчёт.

Машиночитаемые результаты: [ссылки](external-links.json), [image manifests](image-manifests.json), [зависимости](dependency-checks.json), [нативные runtime-пробы](runtime-checks.json), [CPU-библиотеки](cpu-library-checks.json). Статус подготовки курса отделён от [прогресса обучения](../PROGRESS.md).

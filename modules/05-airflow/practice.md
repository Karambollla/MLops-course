# Практика: Airflow: оркестрация ML-пайплайнов

[Теория](README.md) · [Подсказки](hints.md)

## Подготовка

```bash
docker compose -f labs/airflow/compose.yaml up -d --build
docker compose -f labs/airflow/compose.yaml logs --tail=80
```

UI: `http://localhost:8080`. Учётные данные standalone появляются в логах и файле конфигурации auth manager внутри volume; это отдельный локальный стенд. Не используй инструкцию `airflow users create` из старых курсов без проверки Airflow 3.

## Задание 1. DAG без подмены обучения

В `labs/airflow/dags/housing_pipeline.py` реализуй task `train_evaluate`. Рабочие данные внутри контейнера доступны в `/work`; пакет housing уже установлен из исходников при сборке. Создай результат в `/work/runs/RUN_KEY`, передай через XCom только путь и run_key. До реализации task ожидаемо падает.

```bash
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags list-import-errors
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags unpause housing_pipeline
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags trigger housing_pipeline
docker compose -f labs/airflow/compose.yaml exec airflow airflow dags list-runs housing_pipeline
```

Новый DAG по умолчанию paused. Команда unpause разрешает scheduler запускать задачи; trigger без неё может оставить run в queued. После trigger повтори list-runs через несколько секунд и проверь переход в running, затем success после реализации или ожидаемый failed с учебным исключением до неё. Пустая таблица означает, что run не создан или выбран другой DAG.

У учебной task задан `retries=1`; стандартная пауза перед повтором составляет пять минут. Поэтому после первого NotImplementedError можно увидеть `up_for_retry`, пока DAG run ещё running. Смотри состояние и логи конкретной task, а не только общий статус DAG.

## Задание 2. Gate и повтор

Gate читает candidate.test.mae и baseline.test.mae из metrics.json. При отношении больше 0,9 публикация блокируется. Publish сохраняет release manifest с точным путём и версией модели. Запусти один run_key дважды: итоговая опубликованная версия и число смысловых результатов должны остаться прежними.

## Задание 3. Сбой и интервалы

Временно вызови исключение перед publish, повтори только упавший шаг и проверь отсутствие дубликата. Затем добавь ежедневное расписание, передавай интервал в манифест и объясни catchup/backfill на примере двух прошлых дат. Не запускай массовый backfill на ноутбуке.

## Критерии готовности

- [ ] Нет import errors, реальные задачи обучения и оценки завершаются.
- [ ] Плохая модель не публикуется; XCom содержит только метаданные.
- [ ] Retry не создаёт вторую публикацию того же результата.
- [ ] Путь восстановления после искусственного сбоя воспроизводим.

## Завершение

Останови Airflow перед Kubernetes: `docker compose -f labs/airflow/compose.yaml down`. Данные остаются в `work/` и named volume. Удаление volume сбрасывает историю DAG.

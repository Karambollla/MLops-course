# Практика: MLflow: эксперименты и реестр моделей

[Теория](README.md) · [Подсказки](hints.md)

## Подготовка

```bash
docker compose -f labs/mlflow/compose.yaml up -d --build
curl -I http://localhost:5001
```

Порт на ноутбуке — 5001, внутри контейнера — 5000. Это позволяет избежать конфликта с системным сервисом macOS на 5000.

Для SDK используй отдельное окружение с requirements из `labs/mlflow/requirements.txt`; оно включает базовые зависимости проекта. Установи housing в него через `pip install --no-deps -e labs/housing`.

## Задание 1. Три запуска

Доработай `labs/mlflow/track.py`: три разных конфигурации на одном split, параметры, MAE/RMSE, data_sha256, split и model bundle. Сделай таблицу сравнения validation. Не подбирай по test.

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 python labs/mlflow/track.py
```

Ожидаются три завершённых run в experiment `housing-course`. Сохрани run IDs и объяснение выбора.

## Задание 2. Registry

Через `mlflow.sklearn.log_model` зарегистрируй Pipeline с input example и signature. Через MlflowClient назначь `candidate` и `champion`. Разреши champion в конкретный номер версии и сохрани release manifest. Выполни predict через исходный bundle и загруженную зарегистрированную модель на одинаковом batch; результаты должны совпасть в допуске.

## Задание 3. Отказ

Останови сервер и запусти регистрацию ещё раз. Зафиксируй ошибку и выбранную политику сохранения локальных результатов. Запусти сервер обратно и восстанови регистрацию без потери связи с исходным запуском. Не продвигай кандидата автоматически после ошибки.

## Критерии готовности

- [ ] Три run имеют единый split и измеренные метрики.
- [ ] Кандидат выбран по validation, release ссылается на точную версию.
- [ ] После перезапуска сервера метаданные и артефакты доступны.
- [ ] Можно объяснить backend store, artifact store и пределы SQLite.

## Завершение

`docker compose -f labs/mlflow/compose.yaml down` сохраняет volume. Перед `down -v` экспортируй IDs, отчёт и нужные артефакты.

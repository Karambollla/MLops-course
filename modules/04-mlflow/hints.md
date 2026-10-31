# Подсказки: MLflow: эксперименты и реестр моделей

[Вернуться к заданиям](practice.md)

Открывай следующий пункт только после собственной попытки.

1. Подключайся через HTTP tracking URI. Локальный `./mlruns` создаст другой backend, и UI сервера не увидит эти run.
2. Не перепутай sklearn Pipeline с bundle-словарём: registry flavor сохраняет сам Pipeline, а bundle — отдельный artifact проекта.
3. Используй `MlflowClient.set_registered_model_alias` и `get_model_version_by_alias`; проверь API закреплённой версии.
4. Подготовь один run на конфигурацию. Вложенные run допустимы, но для трёх экспериментов не обязательны.
5. Если артефакты пропали после restart, проверь volume и пути `--artifacts-destination`, а не только backend URI.

## Самопроверка

Чем alias отличается от версии? Почему UI не доказывает воспроизводимость? Как восстановить данные при потере backend store? Что произойдёт с уже запущенным API после смены champion?

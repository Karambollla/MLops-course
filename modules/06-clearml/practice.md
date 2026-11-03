# Практика

[Теория](README.md) · [Подсказки](hints.md)

Начинай с README задания: там команды подготовки, зависимости и проверяемые
инварианты. Письменные отчёты и ручные баллы не нужны.

| Задание | Рабочий файл и проверка |
|---|---|
| [Offline train](tasks/01-offline/README.md) | [Заготовка](tasks/01-offline/solution.py) · [тесты](tasks/01-offline/test_task.py) |
| [Server и Agent](tasks/02-agent/README.md) | [Заготовка](tasks/02-agent/README.md) |
| [Сравнение и отказ](tasks/03-comparison-failure/README.md) | [Заготовка](tasks/03-comparison-failure/README.md) |

Проверки Python выполняй из корня репозитория. Инфраструктурные тесты по умолчанию
пропускаются с инструкцией; включай `MLOPS_RUN_INTEGRATION=1` только после подготовки
состояния конкретного задания. С флагом отсутствие зависимостей/конфигурации — ошибка.
Тесты не устанавливают и не удаляют ресурсы. Руководства без тестов содержат
конкретные команды и примеры правильного результата. Примеры не заменяют запуск.

## Уровни проверки

Быстрые unit-тесты подменяют SDK. `MLOPS_RUN_SDK=1 python -m pytest
modules/06-clearml/tasks/01-offline -m sdk -q` выполняет настоящий offline ClearML
1.18.0 в отдельном subprocess и проверяет сохранённые параметры, scalars и
output artifacts на synthetic training fixture. Он не требует work/ и не обучает
за ученика модель. Обязательный запуск собственного housing.train проверяется
отдельно; enqueue/worker/result требует настоящего Server/совместимого Linux
Agent по теме 02. Ни локальный fake, ни offline-сессия не доказывают очередь.

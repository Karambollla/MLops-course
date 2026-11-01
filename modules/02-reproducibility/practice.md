# Практика: Воспроизводимость, данные и DVC

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Технические задания проверяются тестами функций или работающего стенда. Руководства содержат команды и примеры ожидаемого поведения без обязательной письменной сдачи.

| Тема | Файлы и проверка | Платформа |
|---|---|---|
| [Восстановить данные](tasks/01-data-version/README.md) | [Старт](tasks/01-data-version/solution.py) · [Тесты функций](tasks/01-data-version/test_task.py) | cpu |
| [Манифест и контракт](tasks/02-manifest/README.md) | [Старт](tasks/02-manifest/solution.py) · [Тесты функций](tasks/02-manifest/test_task.py) | cpu |
| [Восстановить эксперимент](tasks/03-reproduce/README.md) | [Старт](tasks/03-reproduce/solution.py) · [Тесты функций](tasks/03-reproduce/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=02-reproducibility/01-data-version
```

Подставь идентификатор выбранной темы из README. Незавершённые функции дают ошибки тестов; проверки стенда без включения пропускаются, а для руководств runner показывает путь к материалу. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Функции проверяются на входах и результатах; проверки стенда включаются явно через MLOPS_RUN_INTEGRATION=1. Для руководств открой пример в README, автоматических проверок у них нет.

## Подготовка

Создай отдельное окружение и установи `dvc==3.59.2`. Выполняй команды внутри `work/dvc-demo`, а не в случайном существующем репозитории:

```bash
mkdir -p work/dvc-demo work/dvc-remote
cp work/housing.csv work/dvc-demo/housing.csv
cd work/dvc-demo
git init
dvc init
dvc remote add -d local ../dvc-remote
dvc add housing.csv
dvc push
```

Добавь в Git `.dvc`, `.dvcignore`, `.gitignore` и `housing.csv.dvc`. Commit выполняется после настройки собственного имени и email Git.

## Завершение

Вернись в корень курса. Учебный remote оставь до завершения проекта. Удаление `work/dvc-demo` и `work/dvc-remote` после экспорта отчёта затрагивает только эту лабораторную.

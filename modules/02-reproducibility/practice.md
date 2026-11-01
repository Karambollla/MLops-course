# Практика: Воспроизводимость, данные и DVC

[Теория](README.md) · [Подсказки](hints.md)

## Задания

Каждая папка содержит условие, редактируемую заготовку и собственные тесты. Начинай с README нужной задачи.

| Задание | Основной файл | Платформа |
|---|---|---|
| [Восстановить данные](tasks/01-data-version/README.md) | [Заготовка](tasks/01-data-version/solution.py) · [тесты](tasks/01-data-version/test_task.py) | cpu |
| [Манифест и контракт](tasks/02-manifest/README.md) | [Заготовка](tasks/02-manifest/solution.py) · [тесты](tasks/02-manifest/test_task.py) | cpu |
| [Восстановить эксперимент](tasks/03-reproduce/README.md) | [Заготовка](tasks/03-reproduce/solution.py) · [тесты](tasks/03-reproduce/test_task.py) | cpu |

## Как запускать

Все команды выполняются из корня курса после SETUP:

```bash
make task TASK=02-reproducibility/01-data-version
```

Подставь идентификатор выбранной задачи из её README. Незаполненная заготовка ожидаемо даёт RED. `make test` проверяет готовые компоненты и инструменты курса; задания проверяются отдельно. Для отчётных задач заполняй указанный JSON/Markdown и выполняй ручную рубрику: тест схемы не подтверждает истинность наблюдений.

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

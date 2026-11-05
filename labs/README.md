# Лабораторные заготовки

Учебные заготовки и тесты находятся в `modules/<module>/tasks/<task>/`. Здесь находятся общие стенды, пакет проекта и совместимые входы. Реализации изменяй в папке задания или, для ML, в [notebook](../modules/01-ml/housing.ipynb). `housing.train` загружает определения из этого notebook без выполнения остальных ячеек.

Запускай команды из корня курса. Теория и общая подготовка находятся в README соответствующего модуля. Команды конкретного задания, критерии проверки и остановка стенда описаны в его README.

| Стенд | Назначение | Платформа |
|---|---|---|
| python | Функция и unit-тесты | Mac CPU |
| housing | Данные, учебный train, готовая HTTP-обвязка | Mac CPU |
| mlflow | Tracking server и SDK-задание | Mac CPU. Образ собирается |
| airflow | Standalone и DAG с учебной задачей | Mac CPU. Отдельный ML venv |
| clearml | Offline SDK. Дополнительный Server | Offline — Mac. Server — Linux x86_64 |
| kubernetes / helm | Выкладка собственного image с bundle | kind ARM64 |
| monitoring | Prometheus и provisioned Grafana | Mac CPU |
| vault | Dev server и policy | Mac CPU |
| terraform | Один Docker-контейнер | Mac CPU при доступном daemon |
| ansible | Изолированный Linux-контейнер | Mac CPU |
| qdrant / search | Общий корпус, qrels, отдельные движки | Mac CPU при совместимых image manifests |
| triton | Локальный ONNX. Дополнительный сервер | ONNX — Mac. Server image — Linux x86_64 |
| llm | Расчёты/контракты. Дополнительный serving | NVIDIA-стенды — Linux + GPU |

`TODO(student)` не заменяет теорию: точный контракт и проверка каждого задания находятся в модуле. Эти места должны остаться незавершёнными до твоей реализации. Нельзя получить зачёт только зелёными тестами обвязки с пропущенными учебными тестами.

Для проверки Compose без запуска: `docker compose -f labs/ИМЯ/compose.yaml config --quiet`. Для search/llm имя файла указано в практике. Команда config не доказывает существование image или успешный runtime.

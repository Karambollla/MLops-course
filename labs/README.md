# Лабораторные заготовки

Запускай команды из корня курса. Теория, критерии и cleanup находятся в соответствующем `modules/*/practice.md`.

| Стенд | Назначение | Платформа |
|---|---|---|
| python | Функция и unit-тесты | Mac CPU |
| housing | Данные, учебный train, готовая HTTP-обвязка | Mac CPU |
| mlflow | Tracking server и SDK-задание | Mac CPU; образ собирается |
| airflow | Standalone и DAG с учебной задачей | Mac CPU; отдельный ML venv |
| clearml | Offline SDK; дополнительный Server | Offline — Mac; Server — Linux x86_64 |
| kubernetes / helm | Выкладка собственного image с bundle | kind ARM64 |
| monitoring | Prometheus и provisioned Grafana | Mac CPU |
| vault | Dev server и policy | Mac CPU |
| terraform | Один Docker-контейнер | Mac CPU при доступном daemon |
| ansible | Изолированный Linux-контейнер | Mac CPU |
| qdrant / search | Общий корпус, qrels, отдельные движки | Mac CPU при совместимых image manifests |
| triton | Локальный ONNX; дополнительный сервер | ONNX — Mac; server image — Linux x86_64 |
| llm | Расчёты/контракты; дополнительный serving | NVIDIA-стенды — Linux + GPU |

`TODO(student)` не заменяет теорию: точный контракт и проверка каждого задания находятся в модуле. Эти места должны остаться незавершёнными до твоей реализации. Нельзя получить зачёт только зелёными тестами обвязки с пропущенными учебными тестами.

Для проверки Compose без запуска: `docker compose -f labs/ИМЯ/compose.yaml config --quiet`. Для search/llm имя файла указано в практике. Команда config не доказывает существование image или успешный runtime.

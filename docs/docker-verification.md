# Проверка Docker-лабораторных

Дата: **2026-10-31**. После восстановления daemon выполнены реальные проверки на Docker **29.4.3**, Linux ARM64, 10 CPU и примерно 8 ГБ RAM Docker VM.

## Что проверено

| Стенд | Реальный результат |
|---|---|
| Housing API | Сборка ARM64; 200/422/503; NaN/Infinity дают 422; parity с собственным toy Pipeline; UID 10001; read-only mount; restart |
| Python в контейнере | 6 тестов прошли; 2 учебных пропущены с явной причиной |
| MLflow | Сборка; HTTP tracking; артефакт записан и прочитан; sklearn model/signature; pyfunc predict; alias; данные сохраняются после restart |
| Airflow | Сборка; отдельный ML venv и запись в /work; UI; DAG без import errors; unpause/trigger; validate_data success; ожидаемый NotImplementedError обучения; история после restart |
| Prometheus/Grafana | Scrape; автоматически созданные datasource/dashboard; метрика 20 запросов; alert стал firing после остановки API и снялся после восстановления |
| Vault | Dev server; KV v2; ограниченная policy; разрешённое чтение; запрет чужого пути и записи; истечение token |
| Ansible | Сборка и Linux-запуск; syntax-check; первый запуск changed=2, второй changed=0; результат сохраняется в bind mount |
| Qdrant | Реальный сервер; повторный upsert без дубликатов; фильтр; ошибка размерности; snapshot; восстановление коллекции после restart |
| Elasticsearch | ARM64-запуск; исходный mapping; bulk без item errors; стабильные IDs; keyword/vector top-2; сохранность после restart |
| OpenSearch | Те же проверки на отдельном стенде и том же корпусе; без одновременного запуска с Elasticsearch |
| Terraform | Init/validate; apply; HTTP Nginx; повторный plan без изменений; ручное удаление обнаружено; восстановление; destroy |
| Kubernetes/Helm | kind 0.27.0 + Kubernetes 1.32.2; исходные манифесты и Dockerfile модели; Running без readiness; рабочий Service; ошибка image; Deployment rollback; Helm install/upgrade/rollback и восстановление после неудачного atomic upgrade |

Итого: **9 Compose-стендов**, полный цикл Terraform и отдельный kind-кластер с Helm. Для alert измерено примерно **36.1 с** от остановки API до наблюдения Firing в этой проверке. Это результат функционального теста, а не SLA и не измерение скорости доставки внешних уведомлений. Alertmanager не настраивался.

## Исправления

1. **MLflow:** порт 5000 занят Control Center на этом Mac. Внешний порт заменён на **5001**, внутренний остаётся 5000; track.py и примеры обновлены.
2. **Vault:** при 256 МиБ контейнер завершался с OOMKilled/137. Лимит увеличен до **1 ГиБ**, после чего проверены реальная готовность, policy и TTL. Пусковой пик памяти не измерялся; небольшое потребление после старта не заменяет проверку пуска.
3. **Terraform:** Docker возвращал network_mode=bridge, а незаданный параметр планировался как null и вызывал замену при каждом plan. Явный **network_mode="bridge"** устранил расхождение; ignore_changes не используется.

Загрузки нескольких официальных образов прерывались EOF от registry/CDN. Повторные загрузки завершились успешно; это отделено от функциональных ошибок конфигурации.

## Границы проверки

Использованы временные синтетические sklearn-модели и учебный корпус из восьми документов. Это проверка инфраструктуры, контрактов и восстановления, без результатов качества California Housing или настоящих semantic embeddings. Для Airflow использован временный входной CSV; код обучения/gate/publish остаётся учебным заданием. Ожидаемый отказ TODO не назван успешным обучением.

Дополнительные ClearML Server/Agent и Triton-маршруты для Linux x86_64 не запускались на ARM64 через эмуляцию. TensorRT-LLM, vLLM и SGLang не проверялись без NVIDIA GPU. Предыдущие нативные ONNX и проверки Python-библиотек не выдаются за Docker/GPU runtime.

Студенческие данные в work и основной Terraform state не использовались. Compose-проекты имеют префикс mlops-check, модельные fixtures и Terraform state находились в /tmp, kubeconfig был отдельным. После тестов тестовые контейнеры, volumes и kind-кластер удалены; daemon остаётся доступным. Загруженные базовые образы и build cache сохранены для следующих занятий.

## Как повторять с собственной реализацией

Пройди подготовку своего модуля, используй собственный bundle и команды его practice.md. Минимальные проверки запуска:

```bash
docker compose -f labs/housing/compose.yaml up -d --build
curl -i http://localhost:8000/ready
docker compose -f labs/housing/compose.yaml down

docker compose -f labs/mlflow/compose.yaml up -d --build
curl -i http://localhost:5001/health
docker compose -f labs/mlflow/compose.yaml down
```

Без собственного обученного bundle readiness housing ожидаемо возвращает 503. Для остальных стендов следуй позитивным и негативным сценариям соответствующего модуля. История проверок не является зачётом твоей реализации.

Подробные статусы: [Docker JSON](docker-checks.json). Общая проверка материалов: [verification.md](verification.md).

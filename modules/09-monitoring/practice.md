# Практика: Prometheus, Grafana и качество модели

[Теория](README.md) · [Подсказки](hints.md)

## Подготовка

Останови API другого Compose-стенда и kind при недостатке ресурсов.

```bash
docker compose -f labs/monitoring/compose.yaml up -d --build
```

Prometheus: 9090; Grafana: 3000, локальный вход student / local-course-only. Dashboard Housing course и datasource создаются автоматически. Без модели API жив, но predict даёт 503.

## Задание 1. Нагрузка и dashboard

После подключения собственного bundle отправь 200 запросов с ограниченной конкурентностью 1, затем 4. Измерь RPS, error ratio и p95. Добавь в dashboard панели latency и ошибок. В error ratio учитывай 5xx и дели на число запросов; при нулевом трафике не интерпретируй NaN как успешное обслуживание.

## Задание 2. Отказ

```bash
docker compose -f labs/monitoring/compose.yaml stop api
```

Дождись состояния Firing для HousingTargetDown, сохрани время обнаружения. Запусти API обратно и проверь восстановление. Затем повтори сценарий с живым API без модели: объясни, почему up остаётся 1 и какое дополнительное правило требуется.

## Задание 3. Качество и drift

На фиксированных 500 строках вычисли MAE с target. Создай отдельную копию признаков с контролируемым сдвигом MedInc и сравни квантили с reference. Повтори predict и анализ ошибок. Запиши, какие сигналы доступны без target, а какие требуют labels. Для этого задания не нужен дополнительный monitoring SDK.

## Критерии готовности

- [ ] Prometheus видит API, Grafana показывает собственную нагрузку.
- [ ] Alert обнаруживает и снимает искусственный отказ.
- [ ] Up, готовность модели, ошибки API и качество не смешиваются.
- [ ] Есть runbook и отчёт со временем обнаружения и восстановления.

## Завершение

`docker compose -f labs/monitoring/compose.yaml down`. Перед удалением volume выгрузи свой dashboard JSON и отчёт.

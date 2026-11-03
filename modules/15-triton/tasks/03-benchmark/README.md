# Измерить latency настоящим клиентом

[Теория](../../README.md) · [Практика](../../practice.md)

Сохрани `latency_summary(rows,elapsed_seconds,min_requests=200)`: конечные неотрицательные latency_ms, не меньше min_requests строк и положительное конечное общее wall time. Возвращаются линейные p50_ms/p95_ms по всем строкам, throughput_rps=len(rows)/elapsed_seconds и доля status>=400 error_ratio. Неверные данные — ValueError. Для 10/20/30 ms за 1 s и одной ошибки правильны 20/29 ms, 3 rps, 1/3. Фикстура проверяет арифметику и не является измерением сервера.

Реализуй `benchmark(client,rows,feature_order,requests=200,warmup=5,model_name="housing",output_names=("variable",))`. Это последовательный baseline concurrency=1. Через `load_task("15-triton/02-server").infer` вызови свою SDK-функцию: сначала warmup, затем requests измеряемых вызовов. `requests` должен быть положительным целым, warmup — неотрицательным целым; неверные значения отклоняются до сети. Ошибка во время warmup прекращает эксперимент. Каждый измеряемый вызов измеряется `perf_counter`, включая ошибки; длительность всей измеряемой серии измеряется отдельно.

Возвращаемый контракт: `{"rows":[{"latency_ms":1.2,"status":200},...],"elapsed_seconds":0.5}`. Успеху соответствует status=200; неуспешному измеряемому вызову — синтетический status=500, без текста ответа/исключения. Здесь status — маркер исхода клиента, не попытка восстановить HTTP-код из исключений SDK. Не включай warmup в samples/wall time, не генерируй задержки и не подставляй сумму latency в elapsed_seconds. Перед нагрузкой отдельно проверь численную корректность модели заданием 02.

```bash
make task TASK=15-triton/03-benchmark
python scripts/run_task.py run 15-triton/03-benchmark --rows work/triton/rows.json --requests 200 --warmup 5 --output work/triton/benchmark.json
MLOPS_RUN_INTEGRATION=1 make task TASK=15-triton/03-benchmark
```

CLI создаёт настоящий HTTP SDK client с `TRITON_URL`, вызывает benchmark, применяет latency_summary **к возвращённым сырым замерам** и сохраняет rows/elapsed_seconds/summary в указанный JSON. Выводит summary. Используй существующий JSON-список housing строк; зависимости и платформа — как в задании 02. Fast tests подменяют лишь infer/часы для проверки warmup/ошибок/границ; live probe делает короткую реальную серию твоим клиентом. Только полный CLI-прогон >=200 запросов является baseline benchmark, короткий live probe проверяет взаимодействие.

Сравнивай FastAPI/Triton на одной модели, данных, batch и hardware. Для concurrency=4 нужен отдельный опыт с независимыми клиентами на worker либо согласованным async SDK: `InferenceServerClient` не thread safe, разделять один экземпляр между потоками нельзя. Сохрани сырые CSV/JSON, wall time, версии/ресурсы; файл benchmark.csv содержит только заголовок. Рост throughput при росте p95 требует оценки компромисса, метрики 8002 не заменяют клиентский интервал. Без совместимого Triton не объявляй тесты с doubles измерением сервера.

Останови `docker compose -f labs/triton/compose.yaml down` после опыта.

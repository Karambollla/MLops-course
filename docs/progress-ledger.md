# Ledger — plan: docs/superpowers/plans/2026-10-31-mlops-course.md

Ruling: Работа ведётся в пустой директории пользователя без создания Git/worktree — репозитория нет, пользователь явно указал место результата — история коммитов отсутствует, материалы сохраняются непосредственно здесь.

Ruling: Для учебных Markdown и конфигураций применяются проверки структуры и запусков вместо тестов, зеркалящих текст — это учебный контент; содержательные тесты добавляются к контрактам проекта.

Pre-flight: Модули 01–05 используют общий контракт признаков и артефакта из labs/housing; 07–09 используют image housing:course и порт 8000; 13–14 используют общий корпус и qrels. Контракты фиксируются в заготовках и документах проекта.

Task 1: complete — навигация, два маршрута, окружение, диагностика, словарь, источники; offline check подтверждает целостность.
Task 2: complete — модули 00–03, единый starter, core lock установлен; готовая обвязка 6 PASS, 2 учебных SKIP; opt-in упражнения падают на ожидаемых NotImplementedError.
Task 3: complete — модули 04–06 и отдельные стенды; MLflow native HTTP/SQLite/artifact/registry/alias PASS; Airflow и ClearML runtime честно не подтверждены.
Task 4: complete — модули 07–12; Compose config, Helm lint/render, Terraform init/fmt/validate PASS; Ansible syntax и повтор во временной директории PASS (changed2→0).
Task 5: complete — модули 13–16; image tags проверены, ONNX parity и Qdrant in-memory API PASS; GPU не имитируется.
Task 6: complete — проект, search guide, рубрика, шаблоны и модуль 17 готовы; все ссылки проверены.

Final review: fresh-context reviewer; 3 Important и 2 Minor исправлены одним проходом. Cache bug воспроизведён на реальном Terraform provider и устранён без удаления cache. Документные исправления сверены с первоисточниками; runtime Airflow/Agent не заявляется.

Final: fixed NaN/Infinity validation — test_nonfinite_json_numbers_return_422_instead_of_500 RED→GREEN, suite 6 PASS / 2 expected SKIP.
Final: reviewer set aside student solutions, container/GPU execution, production HA/cloud and toy performance — эти границы прямо установлены спецификацией и отражены в отчёте; заявлений о выполнении нет.

Результат сохраняется в исходной директории пользователя. Git-ветки и коммиты не создаются, поскольку репозитория нет; временные проверочные окружения находятся вне материалов курса.

Final verification: make check PASS (18 модулей, 79 Markdown); pytest 6 PASS / 2 intentional SKIP; markdownlint 0 errors; 66 author-source URLs HTTP OK; 13 Compose config PASS; 22 YAML PASS; 18 image tags exist; Helm lint/render PASS; Terraform validate/fmt PASS вне sandbox (IPC); 5 optional dependency sets resolved.

Docker follow-up 2026-10-31: daemon доступен; 9 Compose-стендов, Python 6 PASS/2 intentional SKIP в Linux-контейнере, Terraform полный цикл и kind/Helm полный rollout/rollback PASS. Исправлены host port MLflow5001, Vault limit1GiB после OOM и явный Terraform network_mode bridge после красного repeat plan. Учебная логика не реализовывалась; см. docs/docker-verification.md.

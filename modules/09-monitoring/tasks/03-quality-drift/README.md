# Качество и drift

Реализуй `analyze(targets, predictions, reference_medinc, shifted_medinc)` в `solution.py`. Объедини target и prediction по ID независимо от порядка. Верни `mae`, `reference_quantiles`, `shifted_quantiles` (q=.1,.5,.9 с линейной интерполяцией), `median_shift` (shifted median минус reference median). При несовпавших множествах ID, дубликатах, пустых выборках и нечисловых/нефинитных значениях — ValueError.

```bash
make task TASK=09-monitoring/03-quality-drift
```

Вход `scenario.json` оставлен для расчётов: MAE=2/3; квантили [1.4,3,4.6] и [3.4,5,6.6]; median_shift=2. Дополнительно примени функцию к собственным prediction/target данным с ID и двум выборкам MedInc. Drift признака сам по себе не доказывает ухудшение MAE: для MAE нужны размеченные targets. Никакой формы наблюдений заполнять не требуется.

Команды запускай из корня курса после [SETUP](../../../../SETUP.md). Python-тесты проверяют функции на фиксированных входах; они не подтверждают запуск стенда. Live-проверки включаются только `MLOPS_RUN_INTEGRATION=1`, читают существующий стенд и не создают/не удаляют ресурсы. При включённом флаге недоступные зависимости — ошибка с подсказкой.

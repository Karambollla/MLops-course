# Практика: ML-сервис, Docker и CI

[Теория](README.md) · [Подсказки](hints.md)

## Задание 1. Контракт

```bash
make test
uvicorn housing.api:app --host 127.0.0.1 --port 8000
```

Без модели проверь `/live` → 200, `/ready` → 503, валидный `/predict` → 503. С обученным bundle `/ready` и `/predict` возвращают 200. Запрос есть в `labs/housing/request.json`.

Добавь интеграционные тесты: совпадение predict HTTP и pipeline, перестановка JSON-ключей, NaN/Infinity, несовместимый bundle и неправильное количество строк. Неверная схема запроса должна давать 422 до выполнения модели.

## Задание 2. Образ

Останови локальный Uvicorn предыдущего задания через Ctrl+C: Compose использует тот же host port 8000.

```bash
docker compose -f labs/housing/compose.yaml config --quiet
docker compose -f labs/housing/compose.yaml up -d --build
curl -i http://localhost:8000/ready
curl -sS http://localhost:8000/predict -H 'Content-Type: application/json' --data-binary @labs/housing/request.json
```

При готовой модели ожидаются 200 и один prediction. Сохрани image ID, версии зависимостей и размер образа. Удали модель только в отдельной временной копии и проверь ожидаемый 503 после перезапуска.

## Задание 3. CI

Прочитай `.github/workflows/check.yml`. В собственном репозитории намеренно сломай контрактный тест в отдельной ветке и убедись, что CI красный. Исправь и проверь зелёный статус. Публикация образа и секреты registry в этом задании не нужны.

## Критерии готовности

- [ ] Результат HTTP соответствует локальному Pipeline.
- [ ] Неверный вход не проходит в модель; отсутствие модели видно через readiness.
- [ ] Контейнер работает без root, данные и секреты не встроены в image.
- [ ] Локальные проверки совпадают с CI-командами.

## Завершение

Останови Uvicorn через Ctrl+C. Для контейнеров: `docker compose -f labs/housing/compose.yaml down`. Артефакты в `work/artifacts` остаются.

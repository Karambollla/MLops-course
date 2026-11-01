# 08. Helm: воспроизводимые релизы

[Программа](../../README.md) · [Практика](practice.md) · [Подсказки](hints.md)

## Цель и вход

Упаковать Deployment/Service в chart, выпускать новые версии через values и проверять откат. Нужен работающий image housing:v1 и локальный Kubernetes. Helm не заменяет знание манифестов: после шаблонизации кластер получает те же ресурсы Kubernetes.

## Chart, values и release

Chart — пакет шаблонов и метаданных. Values — параметры рендера. Release — конкретная установленная копия chart в namespace с историей ревизий. `Chart.yaml version` относится к самому chart; `appVersion` описывает приложение, но автоматически не подставляется в image tag, если шаблон этого не делает.

Отделяй имя релиза, имя приложения и тег image. В заготовке имя Service совпадает с release name. Если установить release `housing-demo`, port-forward к `service/housing` не сработает. Согласованные labels и selectors критичнее красоты шаблона.

## Рендер и проверка

`helm lint` находит часть ошибок chart. `helm template` показывает итоговый YAML без подключения к кластеру. Они не доказывают, что image существует, модель загружается или запрос проходит. Для этого нужны rollout и smoke-test.

```bash
helm template demo modules/08-helm/tasks/01-values/chart -f modules/08-helm/tasks/01-values/values-dev.yaml
```

Проверь число реплик, image, model path и probes в результате. Для строк, которые могут интерпретироваться YAML как число или boolean, используй осознанное quoting. Слишком много вложенных шаблонов ухудшает чтение: для небольшого chart простые ресурсы легче отлаживать.

## Обновление и откат

`helm upgrade --install` создаёт или обновляет release. `--wait` ждёт готовности ресурсов; `--atomic` при неудачном upgrade пытается восстановить предыдущий release. Это не откатывает внешнюю базу данных, mutable S3-объект или события, отправленные приложением. В нашем immutable image находятся и код, и bundle, поэтому rollback возвращает их совместно.

Не используй один mutable tag для разных моделей: узлы могут сохранить старый image. Дай каждому выпуску отдельный тег и запиши digest в release manifest. `imagePullPolicy: Never` используется только в локальном kind после загрузки image; для registry нужна другая политика.

## Окружения и конфигурация

Values-файлы dev и demo могут различаться ресурсами и числом реплик, но не должны содержать секреты. Параметры из `--set` удобны для короткого опыта, а для воспроизводимой поставки лучше сохранять полный набор values и команды. При нескольких `-f` порядок влияет на переопределение значений: не полагайся на память оператора.

Изменение ConfigMap иногда требует checksum-аннотации Pod template, чтобы автоматически запустить rollout. В упражнении реализуй это только после понимания причины. Простое редактирование ConfigMap без перезапуска не обновит переменные процесса.

## Материалы

Все ссылки отобраны 2026-10-31; статус HTTP-проверки — в [отчёте](../../docs/verification.md).

- [Helm quickstart](https://helm.sh/docs/v3/intro/quickstart/) — базовые install/upgrade/rollback для Helm 3.
- [Chart template guide](https://helm.sh/docs/v3/chart_template_guide/) — values, quoting, flow control и debugging.

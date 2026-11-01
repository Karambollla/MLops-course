# 12. Ansible: настройка и идемпотентность

[Программа](../../README.md) · [Практика](practice.md) · [Подсказки](hints.md)

## Цель и вход

Применить конфигурацию дважды и получить отсутствие изменений при повторе. Нужны Linux, YAML и Docker. Управляемая система — отдельный Linux-контейнер; основной macOS не настраивается playbook-ом.

## Inventory, play и task

Inventory определяет hosts и группы. Play связывает hosts, variables и задачи. Task вызывает module: file, copy, template, package, service и другие. В лабораторной controller и managed node находятся в одном контейнере через `ansible_connection=local`. Это упрощает изучение, но не демонстрирует SSH, bastion и управление несколькими узлами.

Модуль знает, как проверить текущее состояние и выполнить нужное изменение. Произвольный `shell: echo ... >> file` каждый раз дописывает строку и не является идемпотентной настройкой. Для записи файла используй copy/template, для директории — file.

```yaml
- name: Ensure example directory exists
  ansible.builtin.file:
    path: /course-output/example
    state: directory
    mode: '0755'
```

## Changed и идемпотентность

`ok` означает, что задача выполнена без изменения, `changed` — состояние изменено. Первый запуск может менять файлы, второй при тех же входах должен давать `changed=0`. Это проверка наблюдаемого поведения; одна зелёная строка PLAY RECAP после первого запуска не доказывает идемпотентность.

Нестабильный template с текущим timestamp будет меняться каждый запуск. Если timestamp действительно нужен как результат выполнения, не смешивай его с желаемой конфигурацией сервиса. Для command/shell существуют `creates`, `removes` и changed_when, но ложное changed_when=false лишь скрывает изменения.

## Variables, templates и handlers

Variables позволяют описывать окружения без копирования playbook. Template подставляет значения в файл. Handler запускается по notify после изменения задачи и обычно используется для перезапуска сервиса. Несколько notify к одному handler в play обычно объединяются; рестарт не нужен после каждого неизменившегося файла.

В учебном контейнере нет systemd, поэтому handler не должен притворяться реальным restart сервиса. Пусть он создаёт диагностический marker или выполняет проверку конфигурации; это проверяет обновление файла, а не работу daemon. Для настоящего daemon нужен соответствующий managed node.

## Check mode и ошибки

`--check --diff` полезен для просмотра изменений, но поддержка зависит от module. Он не заменяет реальное выполнение и не гарантирует отсутствие сетевых side effects у всех задач. Не направляй playbook на чужой inventory ради проверки.

Пароли и токены не должны попадать в diff. Ansible Vault шифрует файлы с переменными, а HashiCorp Vault из модуля 10 — отдельный сервис управления секретами; название похоже, назначение и lifecycle различаются.

## Где проходит граница с Terraform

В проекте Terraform описывает существование локального контейнера, а Ansible — содержимое конфигурации изолированного узла. В production полезно передавать inventory из инфраструктурных outputs, не хранить адреса вручную и разделять права. Не добавляй Ansible к immutable Docker image автоматически: иногда настройку лучше выполнить при сборке image.

## Материалы

- [Ansible getting started](https://docs.ansible.com/projects/ansible/latest/getting_started/index.html) — inventory, playbook и modules.
- [Handlers](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html) — notify и порядок выполнения.
- [Check mode](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html) — возможности и ограничения check/diff.

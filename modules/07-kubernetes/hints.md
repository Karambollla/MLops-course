# Подсказки: Kubernetes: выкладка и диагностика

[Вернуться к заданиям](practice.md)

Открывай следующий пункт только после собственной попытки.

1. В kind локальный image ноутбука не появляется автоматически. Нужен `kind load docker-image` и совпадающий тег.
2. При `imagePullPolicy: Never` отсутствие image даст ErrImageNeverPull, а не попытку скачать его из registry.
3. `kubectl describe pod` содержит events; `kubectl logs --previous` полезен для предыдущего упавшего процесса.
4. Не перепутай прямой port-forward к Pod и проверку готовых endpoints Service.
5. Rollout undo выбирает предыдущую ревизию Deployment. Проверь image и model_version, а не только сообщение об успехе команды.

## Самопроверка

Почему Running не равно Ready? Где хранится bundle? Что произойдёт при превышении memory limit? Что именно восстанавливает rollout undo?

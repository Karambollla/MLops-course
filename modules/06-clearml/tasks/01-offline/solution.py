"""ClearML: реальный offline train — учебная заготовка. Импорт не обращается к инфраструктуре."""

import os


def train_and_log(task):
    """Запусти housing train CLI и зарегистрируй реальные данные/метрики/артефакты."""
    # TODO(student): реализуй контракт из README и тестов.
    raise NotImplementedError("train_and_log")


def main():
    """Без аргументов; CLEARML_OFFLINE_MODE=1 локально по умолчанию; agent всегда online."""
    # Необязательный SDK нужен только для реального запуска, не для сбора тестов.
    from clearml import Task

    Task.set_offline(
        offline_mode=Task.running_locally()
        and os.getenv("CLEARML_OFFLINE_MODE", "1") == "1"
    )
    task = Task.init(project_name="mlops-course", task_name="housing-student")
    task.connect({"seed": 42})
    try:
        return train_and_log(task)
    finally:
        task.close()


if __name__ == "__main__":
    main()

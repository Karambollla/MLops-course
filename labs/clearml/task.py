"""Основной путь — offline SDK без регистрации."""
import os
from clearml import Task

def main():
    # Local runs default to offline; agents must attach to their online task.
    Task.set_offline(offline_mode=Task.running_locally() and os.getenv("CLEARML_OFFLINE_MODE", "1") == "1")
    task = Task.init(project_name="mlops-course", task_name="housing-student")
    task.connect({"seed": 42})
    try:
        # TODO(student): train, real metrics, model artifact and data hash.
        raise NotImplementedError("Подключи реальный эксперимент")
    finally:
        task.close()

if __name__ == "__main__":
    main()

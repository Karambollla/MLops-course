"""Совместимый вход; учебная реализация: modules/06-clearml/tasks/01-offline/solution.py."""
from course_tasks import load_task


def main() -> None:
    return load_task("06-clearml/01-offline").main()


if __name__ == "__main__":
    main()

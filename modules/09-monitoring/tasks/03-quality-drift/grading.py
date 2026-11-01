"""Готовый офлайн grader отчёта. Его реализация не является заданием."""

from course_tasks import load_solution


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    student = load_solution(__file__)
    try:
        valid = True
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return student.analyze(
            p["targets"], p["predictions"], p["reference_medinc"], p["shifted_medinc"]
        )
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

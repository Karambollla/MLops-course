"""Готовый офлайн grader отчёта. Его реализация не является заданием."""

from course_tasks import load_solution


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    student = load_solution(__file__)
    try:
        valid = (
            p["target"] == "api:8000"
            and p["datasource"] == "http://prometheus:9090"
            and p["route"] == "/predict"
            and set(p["panels"]) >= {"rps", "error_ratio", "latency_p95"}
            and p["scrape_up"] == 1
            and len(p["runs"]) == 2
            and [x["concurrency"] for x in p["runs"]] == [1, 4]
            and all(x["requests"] == 200 for x in p["runs"])
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"runs": [student.summarize_run(x) for x in p["runs"]]}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            p["phase"] == "Running"
            and p["ready"] is False
            and p["live_status"] == 200
            and p["ready_status"] == 503
            and p["service_ready_endpoints"] == 0
            and p["image"] == "housing:course"
            and p["model_version"] is None
            and p["readiness_path"] == "/ready"
            and p["liveness_path"] == "/live"
            and any("Readiness" in x and "503" in x for x in p["events"])
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"diagnosis": "model_not_ready", "service_routes_traffic": False}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

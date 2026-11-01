"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def actions(plan):
    rows = [
        x for x in plan["resource_changes"] if x["address"] == "docker_container.web"
    ]
    if len(rows) != 1:
        raise ValueError("Expected docker_container.web once")
    return rows[0]["change"]["actions"]


def noop(plan):
    rows = plan.get("resource_changes", [])
    return isinstance(rows, list) and all(
        x["change"]["actions"] == ["no-op"] for x in rows
    )


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            p["container_name"] == "mlops-course-terraform"
            and bool(p["before_id"])
            and bool(p["restored_id"])
            and p["deleted_container_id"] == p["before_id"] != p["restored_id"]
            and p["configuration_changed"] is False
            and actions(p["drift_plan"]) == ["create"]
            and noop(p["after_plan"])
            and p["http_status"] == 200
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"detected": True, "restored": True}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

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
            p["terraform_version"] == "1.11.4"
            and p["provider_version"] == "3.0.2"
            and p["network_mode"] == "bridge"
            and p["docker_host_unchanged"] is True
            and p["endpoint"] == "http://127.0.0.1:8099"
            and p["http_status"] == 200
            and noop(p["repeat_plan"])
            and actions(p["port_plan"])
            in [["update"], ["delete", "create"], ["create", "delete"]]
            and 1024 <= p["old_port"] <= 65535
            and 1024 <= p["new_port"] <= 65535
            and p["old_port"] != p["new_port"]
            and p["explanation"]
            == ("update" if actions(p["port_plan"]) == ["update"] else "replacement")
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"idempotent": True, "port_action": p["explanation"]}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

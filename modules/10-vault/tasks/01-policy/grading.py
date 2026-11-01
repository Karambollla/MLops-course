"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            p["path"] == "secret/data/housing"
            and p["field"] == "artifact_key"
            and p["field_present"] is True
            and p["read_status"] == 200
            and p["neighbor_status"] == p["write_status"] == 403
            and p["policy_capabilities"] == ["read"]
            and p["token_role"] == "application"
            and p["secret_logged"] is False
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"least_privilege": True}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

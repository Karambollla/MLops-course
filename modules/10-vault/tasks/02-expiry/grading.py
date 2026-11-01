"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    t = p.get("renewable_trial", {}) or {}
    try:
        valid = (
            p["issued_at"] < p["before_at"] < p["expires_at"] <= p["after_at"]
            and p["expires_at"] - p["issued_at"] == 60
            and p["before_status"] == 200
            and p["after_status"] == 403
            and p["renewable"] is False
            and p["renew_status"] == 400
            and t["renewable"] is True
            and t["renew_status"] == 200
            and 0 < t["ttl_before"] < t["ttl_after"]
            and t["revoke_status"] == 204
            and t["read_after_revoke"] == 403
            and p["max_attempts"] == 1
            and p["timeout_class"] == "network_timeout"
            and p["auth_class"] == "access_denied"
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"expired": True, "revoked": True}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

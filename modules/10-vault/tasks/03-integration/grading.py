"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            p["pod_uses_root"] is False
            and p["kv_is_dynamic"] is False
            and (
                (
                    p["use_case"] == "local_read_only"
                    and p["secret_needed"] is False
                    and p["auth_method"] == "none"
                )
                or (
                    p["use_case"] in ["private_artifact", "external_dependency"]
                    and p["secret_needed"] is True
                    and p["auth_method"] == "kubernetes"
                    and all(
                        p["identity"][k]
                        for k in ["namespace", "service_account", "role"]
                    )
                    and p["secret_zero"] == "service_account_jwt"
                    and p["policy_path"] == "secret/data/housing"
                    and p["capabilities"] == ["read"]
                    and p["ttl_seconds"] > 0
                    and p["on_expiry"] in ["unready", "stop"]
                    and p["rotation"] in ["reload_on_renewal", "restart"]
                )
            )
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"requires_vault": p["secret_needed"]}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

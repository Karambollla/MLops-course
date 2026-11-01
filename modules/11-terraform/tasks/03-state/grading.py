"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            set(p["state_addresses"]) == {"docker_image.web", "docker_container.web"}
            and bool(p["state_container_id"])
            and p["state_container_id"] == p["observed_container_id"] == p["import_id"]
            and p["import_address"] == "docker_container.web"
            and p["terraform_version"] == "1.11.4"
            and p["provider_version"] == "3.0.2"
            and p["tracked_in_git"] is False
            and p["state_may_contain_secrets"] is True
            and p["sensitive_encrypts_state"] is False
            and p["lost_state_plan_actions"] == ["create"]
            and p["team_backend"]
            == {"remote": True, "locking": True, "access_control": True}
            and p["roles"]
            == {
                "configuration": "desired_state",
                "state": "resource_bindings",
                "lock_file": "provider_versions_checksums",
            }
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"bindings_consistent": True, "team_backend_ready": True}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

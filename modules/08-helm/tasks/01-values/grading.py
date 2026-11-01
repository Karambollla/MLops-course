"""Готовый офлайн grader отчёта. Его реализация не является заданием."""

import re


def sha(value, length=64):
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-fA-F]{%d}" % length, value) is not None
    )


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            bool(p["release_name"])
            and p["release_name"] == p["service_name"]
            and p["image"] == "housing:v1"
            and p["replicas"] == 1
            and 0 < p["request_memory_mib"] <= p["limit_memory_mib"] <= 1024
            and bool(p["config_before"])
            and bool(p["config_after"])
            and p["config_before"] != p["config_after"]
            and sha(p["checksum_before"])
            and sha(p["checksum_after"])
            and p["checksum_before"] != p["checksum_after"]
            and p["checksum_location"] == "spec.template.metadata.annotations"
            and {"ConfigMap.data", "Deployment.spec.template.metadata.annotations"}
            <= set(p["render_changed_fields"])
            and p["ready"] is True
            and p["predict_status"] == 200
            and bool(p["model_version"])
            and p["model_version"] == p["expected_model_version"]
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"rollout_required": True, "service_name": p["service_name"]}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

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
            bool(p["release_id"])
            and p["image"] == "housing:v1"
            and p["image_digest"].startswith("sha256:")
            and sha(p["image_digest"][7:])
            and p["ready_replicas"] == p["desired_replicas"] >= 1
            and p["predict_status"] == 200
            and bool(p["model_version"])
            and p["model_version"] == p["expected_model_version"]
            and p["service_ready_endpoints"] >= 1
            and bool(p["configmap"])
            and p["configmap"] == p["pod_env"]
            and p["config_revision"] == p["pod_config_revision"]
            and 0 < p["memory_request_mib"] <= p["memory_limit_mib"] <= 1024
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"model_version": p["model_version"], "ready": True}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

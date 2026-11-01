"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            p["stopped_at"]
            <= p["pending_at"]
            < p["firing_at"]
            <= p["restarted_at"]
            < p["resolved_at"]
            and p["firing_at"] - p["pending_at"] >= p["for_seconds"] > 0
            and p["alert"] == "HousingTargetDown"
            and p["states"] == ["inactive", "pending", "firing", "inactive"]
            and p["down_up"] == 0
            and p["recovered_up"] == 1
            and p["no_model"] == {"up": 1, "ready_status": 503, "predict_status": 503}
            and p["additional_alert"] == "model_readiness_or_predict_5xx"
            and all(
                p["runbook"][k] for k in ["symptom", "check", "recovery", "success"]
            )
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {
            "detection_seconds": p["firing_at"] - p["stopped_at"],
            "recovery_seconds": p["resolved_at"] - p["restarted_at"],
        }
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

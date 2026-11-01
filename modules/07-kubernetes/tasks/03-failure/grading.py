"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            p["failure_image"] == "housing:missing"
            and p["event"]
            == (
                "ErrImageNeverPull"
                if p["pull_policy"] == "Never"
                else "ImagePullBackOff"
            )
            and p["failed_ready"] is False
            and p["rollback_image"] == "housing:v1"
            and bool(p["rollback_model"])
            and p["rollback_model"] == p["expected_model"]
            and p["rollback_ready"] is True
            and p["predict_status"] == 200
            and p["diagnoses"]
            == {
                "Pending": "scheduling",
                "CrashLoopBackOff": "process_crash",
                "RunningNotReady": "readiness",
                "OOMKilled": "memory_limit",
            }
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"restored": True, "image_failure": p["event"]}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

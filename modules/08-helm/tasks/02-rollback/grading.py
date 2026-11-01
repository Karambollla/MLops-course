"""Готовый офлайн grader отчёта. Его реализация не является заданием."""


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            bool(p["release_name"])
            and p["upgrade_exit"] != 0
            and p["failed_image"] == "housing:missing"
            and p["atomic"] is True
            and p["before_revision"]
            < p["failed_revision"]
            < p["restored_revision"]
            < p["v2_revision"]
            < p["manual_rollback_revision"]
            and p["selected_rollback_target"] == p["before_revision"]
            and bool(p["before_model"])
            and p["before_model"] == p["after_atomic_model"] == p["after_manual_model"]
            and p["v2_model"] != p["before_model"]
            and p["predict_statuses"] == [200, 200, 200]
            and p["history_statuses"]
            == ["superseded", "failed", "superseded", "superseded", "deployed"]
            and p["external_state_rolled_back"] is False
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"atomic_restored": True, "manual_restored": True}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

"""Готовый офлайн grader отчёта. Его реализация не является заданием."""

import math
import re


def sha(value, length=64):
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-fA-F]{%d}" % length, value) is not None
    )


def metric(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


def validate_report(p):
    if not isinstance(p, dict):
        raise ValueError("Отчёт должен быть JSON-объектом")
    f = p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            bool(p["mlflow_run_id"])
            and bool(p["clearml_task_id"])
            and sha(p["data_sha256"])
            and metric(p["mlflow_mae"])
            and abs(p["mlflow_mae"] - p["clearml_mae"]) <= 1e-8
            and p["parameters_equal"] is True
            and p["artifacts_equal"] is True
            and len(set(p["maintenance_tradeoffs"])) >= 2
            and p["ownership"]
            == {
                "tracking": ["mlflow", "clearml"],
                "schedule": "airflow",
                "execution": "clearml-agent",
            }
            and f["injected_at"] <= f["observed_at"] < f["recovered_at"]
            and (
                (
                    p["mode"] == "offline"
                    and f["session_saved"] is True
                    and f["queue_tested"] is False
                )
                or (
                    p["mode"] == "agent"
                    and f["queue_tested"] is True
                    and bool(f["agent_id"])
                    and f["task_state_before"] != f["task_state_after"]
                )
            )
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {
            "level": p["mode"],
            "detection_seconds": f["observed_at"] - f["injected_at"],
        }
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

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
    p.get("failure", {}) or {}
    p.get("renewable_trial", {}) or {}
    try:
        valid = (
            p["mode"] == "online"
            and bool(p["task_id"])
            and p["task_id"] != p["clone_of"]
            and p["queue"] == "default"
            and bool(p["agent_id"])
            and p["states"] == ["queued", "in_progress", "completed"]
            and sha(p["code_commit"], 40)
            and p["data_source"].startswith(("https://", "s3://", "/"))
            and not p["data_source"].startswith("/Users/")
            and sha(p["data_sha256"])
            and metric(p["metrics"]["mae"])
            and "model.joblib" in p["artifacts"]
            and all(p[k] == 200 for k in ["web_status", "api_status", "files_status"])
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"remote_execution": True, "task_id": p["task_id"]}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

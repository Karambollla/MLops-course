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
            p["mode"] == "offline"
            and p["seed"] == 42
            and sha(p["data_sha256"])
            and metric(p["metrics"]["mae"])
            and metric(p["metrics"]["rmse"])
            and p["metrics"]["rmse"] >= p["metrics"]["mae"]
            and {"model.joblib", "manifest.json"} <= set(p["artifacts"])
            and bool(p["session_path"])
            and p["train_exit_code"] == 0
        )
        if not valid:
            raise ValueError("Неполные или противоречивые наблюдения; см. README")
        return {"mode": "offline", "mae": p["metrics"]["mae"]}
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError("Неверная схема отчёта") from exc

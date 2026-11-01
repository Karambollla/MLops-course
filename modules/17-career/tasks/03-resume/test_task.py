import json
import math
from pathlib import Path

from course_tasks import course_root


def test_portfolio_has_own_evidence_and_consistent_numeric_claims():
    report = json.loads(Path(__file__).with_name("portfolio.json").read_text())
    assert len(report["bullets"]) == 3, "Подготовь три собственных пункта резюме"
    for row in report["bullets"]:
        assert isinstance(row["text"], str) and row["text"].strip()
        assert isinstance(row["evidence_path"], str) and row["evidence_path"].strip()
        assert (course_root() / row["evidence_path"]).is_file(), (
            "Доказательство должно существовать локально"
        )
        comparison = row.get("comparison")
        if comparison is not None:
            before, after = comparison["baseline"], comparison["candidate"]
            assert before > 0 and math.isfinite(before) and math.isfinite(after)
            expected = (
                (before - after if comparison["lower_is_better"] else after - before)
                / before
                * 100
            )
            assert math.isclose(
                comparison["percent"], expected, rel_tol=1e-5, abs_tol=0.01
            )
    assert len(report["vacancies"]) >= 10
    assert all(
        row["title"]
        and row["url"].startswith(("https://", "http://"))
        and row["requirements"]
        for row in report["vacancies"]
    )
    assert report["skills"] and len(report["next_steps"]) == 3
    assert all(isinstance(step, str) and step.strip() for step in report["next_steps"])

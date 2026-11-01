import json
from pathlib import Path


def test_every_question_has_an_answer_and_a_project_example():
    rows = json.loads(Path(__file__).with_name("answers.json").read_text())
    assert len(rows) == 12 and {r["id"] for r in rows} == set(range(1, 13))
    for row in rows:
        for key in ["answer", "project_example", "verification"]:
            assert (
                isinstance(row[key], str)
                and row[key].strip()
                and "TODO" not in row[key]
            ), f"Вопрос{row['id']}: заполни {key}"

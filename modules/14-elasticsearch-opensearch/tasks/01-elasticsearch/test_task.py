import json

import pytest
from course_tasks import load_solution

s = load_solution(__file__)
DOCS = [
    {"id": 1, "text": "Rollback", "topic": "release", "vector": [1.0, 0.0, 0.0, 0.0]}
]


def test_bulk_uses_stable_ids_ndjson_and_final_newline():
    text = s.build_bulk(DOCS, "course-docs")
    assert text.endswith("\n")
    lines = [json.loads(line) for line in text.splitlines()]
    assert lines == [
        {"index": {"_index": "course-docs", "_id": "1"}},
        {k: DOCS[0][k] for k in ["text", "topic", "vector"]},
    ]
    assert s.build_bulk(DOCS, "course-docs") == text


def test_bulk_checks_each_item_even_when_http_was_ok():
    response = {
        "errors": True,
        "items": [
            {"index": {"_id": "1", "status": 201}},
            {
                "index": {
                    "_id": "2",
                    "status": 400,
                    "error": {"type": "mapper_parsing_exception"},
                }
            },
        ],
    }
    assert s.bulk_failures(response) == ["2"]
    assert (
        s.bulk_failures(
            {"errors": False, "items": [{"index": {"_id": "1", "status": 200}}]}
        )
        == []
    )


def test_duplicate_ids_and_empty_index_are_rejected():
    with pytest.raises(ValueError):
        s.build_bulk(DOCS + DOCS, "course-docs")
    with pytest.raises(ValueError):
        s.build_bulk(DOCS, "")

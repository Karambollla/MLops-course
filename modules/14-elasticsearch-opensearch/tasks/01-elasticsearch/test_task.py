import json
import os
from urllib.request import Request, urlopen

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


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1",
    reason="Нужен уже загруженный поисковый индекс course-docs",
)
def test_live_index_and_search_return_original_security_documents():
    base = os.environ["ELASTICSEARCH_URL"].rstrip("/")

    def read(path, body=None):
        request = Request(
            base + "/course-docs" + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            return json.load(response)

    assert read("/_count")["count"] == 8
    result = read(
        "/_search",
        {
            "knn": {
                "field": "vector",
                "query_vector": [0, 0, 0, 1],
                "k": 2,
                "num_candidates": 8,
            },
            "size": 2,
        },
    )
    hits = result["hits"]["hits"]
    assert {hit["_id"] for hit in hits} == {"7", "8"}
    assert all(hit["_source"]["topic"] == "security" for hit in hits)
    lexical = read("/_search", {"query": {"match": {"text": "Vault"}}})
    assert "7" in {hit["_id"] for hit in lexical["hits"]["hits"]}


def test_bulk_multiple_unicode_documents_keep_action_source_pairs():
    docs = [
        {"id": 42, "text": "Привет\nмир 🔑", "topic": "安全", "vector": [1, 2]},
        {"id": 0, "text": "Second", "topic": "release", "vector": [3, 4]},
    ]
    output = s.build_bulk(docs, "unicode-docs")
    assert output.endswith("\n")
    lines = output.splitlines()
    assert len(lines) == 4
    parsed = [json.loads(line) for line in lines]
    for position, doc in enumerate(docs):
        assert parsed[2 * position] == {
            "index": {"_index": "unicode-docs", "_id": str(doc["id"])}
        }
        assert parsed[2 * position + 1] == {
            key: doc[key] for key in ("text", "topic", "vector")
        }
    assert [
        json.loads(line) for line in s.build_bulk(docs, "unicode-docs").splitlines()
    ] == parsed


def test_bulk_failure_items_override_top_level_flag_and_include_all_failures():
    items = [
        {"index": {"_id": "a", "status": 299}},
        {"index": {"_id": "b", "status": 300}},
        {"index": {"_id": "c", "status": 201, "error": {"type": "rejected"}}},
        {"index": {"_id": "d", "status": 503}},
    ]
    assert s.bulk_failures({"errors": False, "items": items}) == ["b", "c", "d"]
    assert s.bulk_failures({"errors": True, "items": [items[0]]}) == []
    assert s.bulk_failures({"errors": True, "items": []}) == []

import copy
import json
from pathlib import Path
from uuid import uuid4
import os
from urllib.request import Request, urlopen

import pytest
from course_tasks import load_solution, load_task

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


@pytest.mark.integration
@pytest.mark.writes
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1" or os.getenv("MLOPS_RUN_WRITES") != "1",
    reason="Set both MLOPS_RUN_INTEGRATION=1 and MLOPS_RUN_WRITES=1",
)
def test_live_student_sdk_ingest_and_search_in_owned_index():
    assert s.Elasticsearch is not None, "Install labs/search/requirements.txt"
    client = s.Elasticsearch(os.environ["ELASTICSEARCH_URL"])
    index = "mlops-test-elasticsearch-" + uuid4().hex
    # Reserve the unique name before letting the student implementation touch it.
    assert not client.indices.exists(index=index)
    corpus = Path(__file__).resolve().parents[4] / "labs/search/corpus.json"
    documents = json.loads(corpus.read_text(encoding="utf-8"))
    mapping = json.loads(Path(__file__).with_name("mapping.json").read_text())
    try:
        s.ensure_index(client, index, mapping)
        s.ensure_index(client, index, mapping)
        assert s.ingest_documents(client, index, documents) == 8
        assert s.ingest_documents(client, index, documents) == 8
        assert client.count(index=index)["count"] == 8
        actual_mapping = client.indices.get_mapping(index=index)[index]["mappings"]
        expected_properties = mapping["mappings"]["properties"]
        for field in ("text", "topic", "vector"):
            for key, value in expected_properties[field].items():
                actual = actual_mapping["properties"][field][key]
                if isinstance(value, dict):
                    assert all(
                        actual[setting] == expected
                        for setting, expected in value.items()
                    )
                else:
                    assert actual == value
        incompatible = copy.deepcopy(mapping)
        vector_mapping = incompatible["mappings"]["properties"]["vector"]
        vector_mapping["dims" if "dims" in vector_mapping else "dimension"] = 3
        with pytest.raises(ValueError):
            s.ensure_index(client, index, incompatible)
        assert client.count(index=index)["count"] == 8
        stored = client.search(
            index=index, body={"size": 100, "query": {"match_all": {}}}
        )
        assert {int(hit["_id"]): hit["_source"] for hit in stored["hits"]["hits"]} == {
            doc["id"]: {key: doc[key] for key in ("text", "topic", "vector")}
            for doc in documents
        }
        lexical = s.lexical_search(client, index, "Vault", k=5)
        assert 7 in [hit["id"] for hit in lexical]
        vector = s.vector_search(client, index, [0, 0, 0, 1], k=2, topic="security")
        assert {hit["id"] for hit in vector} == {7, 8}
        assert all(hit["payload"]["topic"] == "security" for hit in vector)
        assert all(isinstance(hit["score"], (float, int)) for hit in vector)
        assert s.vector_search(client, index, [0, 0, 0, 1], k=2, topic="missing") == []
        assert s.lexical_search(client, index, "Vault", topic="release") == []
        with pytest.raises(ValueError):
            s.vector_search(client, index, [1, 0], k=2)

        metrics = load_task("13-qdrant/02-evaluation")
        rrf = load_task("14-elasticsearch-opensearch/03-comparison")
        lexical_ids = [hit["id"] for hit in lexical]
        vector_ids = [hit["id"] for hit in vector]
        fused = rrf.reciprocal_rank_fusion([lexical_ids, vector_ids])
        assert {row["id"] for row in fused} == set(lexical_ids + vector_ids)
        assert metrics.ranking_metrics(vector_ids, [7, 8], 2) == {
            "recall": 1.0,
            "precision": 1.0,
            "mrr": 1.0,
        }
        assert (
            metrics.ranking_metrics([row["id"] for row in fused], [7, 8], 2)["recall"]
            == 1.0
        )
        invalid = {
            "id": 900,
            "text": {"invalid": "object"},
            "topic": "security",
            "vector": [0, 0, 0, 1],
        }
        with pytest.raises(ValueError, match="900"):
            s.ingest_documents(client, index, [documents[0], invalid])
        assert client.count(index=index)["count"] == 8
    finally:
        if client.indices.exists(index=index):
            client.indices.delete(index=index)
        client.close()

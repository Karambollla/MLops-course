import copy
import json
from pathlib import Path
from uuid import uuid4
import os
from urllib.request import Request, urlopen

import pytest
from course_tasks import load_solution, load_task

s = load_solution(__file__)


def test_opensearch_query_uses_correct_shape_and_filter():
    vector = [1.0, 0.0, 0.0, 0.0]
    assert s.knn_request(vector, 2) == {
        "size": 2,
        "query": {"knn": {"vector": {"vector": vector, "k": 2}}},
    }
    result = s.knn_request(vector, 2, topic="security")
    assert result["query"]["knn"]["vector"]["filter"] == {"term": {"topic": "security"}}
    assert "post_filter" not in result


@pytest.mark.parametrize(
    "vector,k",
    [
        ([1.0], 2),
        ([0.0] * 4, 2),
        ([float("nan"), 0, 0, 1], 2),
        ([1, 0, 0, 0], 0),
        ([1, 0, 0, 0], True),
    ],
)
def test_invalid_query_is_rejected_before_request(vector, k):
    with pytest.raises(ValueError):
        s.knn_request(vector, k)


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1",
    reason="Нужен уже загруженный поисковый индекс course-docs",
)
def test_live_index_and_search_return_original_security_documents():
    base = os.environ["OPENSEARCH_URL"].rstrip("/")

    def read(path, body=None):
        request = Request(
            base + "/course-docs" + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            return json.load(response)

    assert read("/_count")["count"] == 8
    result = read("/_search", s.knn_request([0, 0, 0, 1], 2, topic="security"))
    hits = result["hits"]["hits"]
    assert {hit["_id"] for hit in hits} == {"7", "8"}
    assert all(hit["_source"]["topic"] == "security" for hit in hits)
    lexical = read("/_search", {"query": {"match": {"text": "Vault"}}})
    assert "7" in {hit["_id"] for hit in lexical["hits"]["hits"]}


@pytest.mark.parametrize("topic", [None, "security"])
def test_custom_embedding_dimension_and_topic_presence(topic):
    result = s.knn_request([0.5, -1], 7, topic=topic, dimension=2)
    expected = {"vector": [0.5, -1], "k": 7}
    if topic is not None:
        expected["filter"] = {"term": {"topic": topic}}
    assert result == {"size": 7, "query": {"knn": {"vector": expected}}}


@pytest.mark.parametrize(
    "vector,k,dimension",
    [
        ([], 1, 4),
        ([1, float("inf")], 1, 2),
        ([1, -float("inf")], 1, 2),
        ([1, 2], 1, 3),
        ([0, 0], 1, 2),
        ([1, 2], -1, 2),
        ([1, 2], 1.5, 2),
    ],
)
def test_documented_bad_custom_queries(vector, k, dimension):
    with pytest.raises(ValueError):
        s.knn_request(vector, k, dimension=dimension)


@pytest.mark.integration
@pytest.mark.writes
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1" or os.getenv("MLOPS_RUN_WRITES") != "1",
    reason="Set both MLOPS_RUN_INTEGRATION=1 and MLOPS_RUN_WRITES=1",
)
def test_live_student_sdk_ingest_and_search_in_owned_index():
    assert s.OpenSearch is not None, "Install labs/search/requirements.txt"
    client = s.OpenSearch(os.environ["OPENSEARCH_URL"])
    index = "mlops-test-opensearch-" + uuid4().hex
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
        settings = client.indices.get_settings(index=index)[index]["settings"]["index"]
        assert settings["knn"] in (True, "true")
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

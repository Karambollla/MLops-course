import json
import os
from urllib.request import Request, urlopen

import pytest
from course_tasks import load_solution

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

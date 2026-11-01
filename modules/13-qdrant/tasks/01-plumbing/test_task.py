import copy
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from course_tasks import load_solution

s = load_solution(__file__)
DOC = {"id": 7, "text": "Vault policy", "topic": "security", "vector": [0.0, 1.0]}


def test_points_preserve_ids_vectors_and_payload():
    points = s.build_points([DOC])
    assert points == [
        {
            "id": 7,
            "vector": [0.0, 1.0],
            "payload": {"text": "Vault policy", "topic": "security"},
        }
    ]
    assert s.build_points([DOC]) == points


@pytest.mark.parametrize(
    "docs",
    [
        [DOC, DOC],
        [{**DOC, "id": True}],
        [{**DOC, "id": "7"}],
        [{**DOC, "id": -1}],
        [{**DOC, "vector": [float("nan"), 1]}],
        [{**DOC, "vector": [0, 0]}],
        [DOC, {**DOC, "id": 8, "vector": [1, 2, 3]}],
    ],
)
def test_bad_ids_and_vector_geometry_are_rejected(docs):
    with pytest.raises(ValueError):
        s.build_points(copy.deepcopy(docs))


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1",
    reason="Нужен работающий Qdrant с коллекцией course-docs",
)
def test_live_collection_contains_original_eight_points():
    url = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
    with urlopen(url + "/collections/course-docs", timeout=5) as response:
        data = json.load(response)
    assert data["result"]["points_count"] == 8

    def query(body):
        request = Request(
            url + "/collections/course-docs/points/query",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            return json.load(response)["result"]["points"]

    points = query({"query": [0, 0, 0, 1], "limit": 2, "with_payload": True})
    assert {p["id"] for p in points} == {7, 8}
    points = query(
        {
            "query": [0, 0, 0, 1],
            "limit": 8,
            "with_payload": True,
            "filter": {"must": [{"key": "topic", "match": {"value": "security"}}]},
        }
    )
    assert {p["id"] for p in points} == {7, 8}
    assert all(p["payload"]["topic"] == "security" for p in points)
    with pytest.raises(HTTPError) as error:
        query({"query": [1, 0], "limit": 2})
    assert error.value.code == 400

import copy
import json
import os
from urllib.request import urlopen

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
        [{**DOC, "vector": [float("nan"), 1]}],
        [{**DOC, "vector": [0, 0]}],
        [DOC, {**DOC, "id": 8, "vector": [1, 2, 3]}],
    ],
)
def test_bad_ids_and_vector_geometry_are_rejected(docs):
    with pytest.raises(ValueError):
        s.build_points(copy.deepcopy(docs))


@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1",
    reason="Нужен работающий Qdrant с коллекцией course-docs",
)
def test_live_collection_contains_original_eight_points():
    url = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
    with urlopen(url + "/collections/course-docs", timeout=5) as response:
        data = json.load(response)
    assert data["result"]["points_count"] == 8

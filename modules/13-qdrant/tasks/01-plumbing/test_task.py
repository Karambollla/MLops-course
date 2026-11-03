import copy
import json
import os
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from course_tasks import load_solution, load_task

try:
    from qdrant_client import QdrantClient, models
except ModuleNotFoundError as exc:
    if exc.name != "qdrant_client":
        raise
    QdrantClient = models = None

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


def test_multiple_points_keep_payload_attached_to_original_ids():
    docs = [
        {"id": 0, "text": "Ключ 🔑", "topic": "安全", "vector": [1, -2, 3]},
        {"id": 42, "text": "Second", "topic": "release", "vector": [-1, 0, 2]},
    ]
    assert s.build_points(docs) == [
        {
            "id": d["id"],
            "vector": d["vector"],
            "payload": {"text": d["text"], "topic": d["topic"]},
        }
        for d in docs
    ]


@pytest.mark.parametrize("invalid_id", [False, None, 1.5, {}, []])
def test_other_invalid_ids_raise_value_error(invalid_id):
    with pytest.raises(ValueError):
        s.build_points([{**DOC, "id": invalid_id}])


@pytest.mark.parametrize(
    "vector", [[], [float("inf"), 1], [1, -float("inf")], ["x", 1]]
)
def test_remaining_bad_point_geometry(vector):
    with pytest.raises(ValueError):
        s.build_points([{**DOC, "vector": vector}])


@pytest.fixture
def local_qdrant(monkeypatch):
    assert QdrantClient is not None, (
        "MLOPS_RUN_SDK=1 requires python -m pip install -r labs/qdrant/requirements.txt"
    )
    assert version("qdrant-client") == "1.13.3", "Install labs/qdrant/requirements.txt"
    client = QdrantClient(":memory:")

    class ClientView:
        # Student code may close its client; retain the in-memory store for inspection.
        def __getattr__(self, name):
            return getattr(client, name)

        def close(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    monkeypatch.setattr(s, "QdrantClient", lambda *args, **kwargs: ClientView())
    monkeypatch.setattr(s, "models", models)
    try:
        yield client
    finally:
        client.close()


@pytest.mark.sdk
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_SDK") != "1", reason="Set MLOPS_RUN_SDK=1 for local Qdrant SDK"
)
def test_sdk_index_documents_upserts_actual_points_idempotently(local_qdrant, tmp_path):
    corpus = Path(__file__).resolve().parents[4] / "labs/search/corpus.json"
    documents = json.loads(corpus.read_text(encoding="utf-8"))
    local_corpus = tmp_path / "corpus.json"
    local_corpus.write_text(json.dumps(documents), encoding="utf-8")
    s.index_documents("http://unused.invalid:6333", local_corpus)
    s.index_documents("http://unused.invalid:6333", local_corpus)
    assert local_qdrant.count("course-docs", exact=True).count == 8
    points, _ = local_qdrant.scroll(
        "course-docs", limit=100, with_vectors=True, with_payload=True
    )
    assert {point.id for point in points} == {doc["id"] for doc in documents}
    by_id = {point.id: point for point in points}
    for doc in documents:
        point = by_id[doc["id"]]
        assert point.payload == {"text": doc["text"], "topic": doc["topic"]}
        # Cosine collections store normalized vectors.
        norm = sum(value * value for value in doc["vector"]) ** 0.5
        assert point.vector == pytest.approx([value / norm for value in doc["vector"]])
    schema = local_qdrant.get_collection("course-docs").config.params.vectors
    assert schema.size == 4
    assert schema.distance == models.Distance.COSINE
    result = local_qdrant.query_points(
        "course-docs", query=[0, 0, 0, 1], limit=2
    ).points
    assert {point.id for point in result} == {7, 8}
    filtered = local_qdrant.query_points(
        "course-docs",
        query=[0, 0, 0, 1],
        limit=8,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="topic",
                    match=models.MatchValue(value="security"),
                )
            ]
        ),
    ).points
    assert {point.id for point in filtered} == {7, 8}
    assert all(point.payload["topic"] == "security" for point in filtered)


@pytest.mark.sdk
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_SDK") != "1", reason="Set MLOPS_RUN_SDK=1 for local Qdrant SDK"
)
def test_sdk_incompatible_schema_refuses_safely_or_really_indexes(
    local_qdrant, tmp_path
):
    local_qdrant.create_collection(
        "course-docs",
        vectors_config=models.VectorParams(size=3, distance=models.Distance.COSINE),
    )
    local_qdrant.upsert(
        "course-docs",
        points=[
            models.PointStruct(
                id=999,
                vector=[1.0, 0.0, 0.0],
                payload={"text": "Existing point", "topic": "original"},
            )
        ],
    )
    original, _ = local_qdrant.scroll(
        "course-docs", limit=100, with_vectors=True, with_payload=True
    )
    corpus = Path(__file__).resolve().parents[4] / "labs/search/corpus.json"
    documents = json.loads(corpus.read_text(encoding="utf-8"))
    local_corpus = tmp_path / "corpus.json"
    local_corpus.write_bytes(corpus.read_bytes())
    try:
        s.index_documents("http://unused.invalid:6333", local_corpus)
    except NotImplementedError:
        raise
    except Exception:
        # Both explicit preflight checks and SDK errors may reject the schema.
        remaining, _ = local_qdrant.scroll(
            "course-docs", limit=100, with_vectors=True, with_payload=True
        )
        assert remaining == original
        schema = local_qdrant.get_collection("course-docs").config.params.vectors
        assert schema.size == 3 and schema.distance == models.Distance.COSINE
    else:
        schema = local_qdrant.get_collection("course-docs").config.params.vectors
        assert schema.size == 4 and schema.distance == models.Distance.COSINE
        assert local_qdrant.count("course-docs", exact=True).count == len(documents)
        points, _ = local_qdrant.scroll(
            "course-docs", limit=100, with_vectors=True, with_payload=True
        )
        by_id = {point.id: point for point in points}
        assert set(by_id) == {doc["id"] for doc in documents}
        for doc in documents:
            point = by_id[doc["id"]]
            assert point.payload == {"text": doc["text"], "topic": doc["topic"]}
            norm = sum(value * value for value in doc["vector"]) ** 0.5
            assert point.vector == pytest.approx(
                [value / norm for value in doc["vector"]]
            )


@pytest.mark.sdk
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_SDK") != "1", reason="Set MLOPS_RUN_SDK=1 for local Qdrant SDK"
)
def test_sdk_student_query_filters_and_uses_named_collection(local_qdrant):
    corpus = Path(__file__).resolve().parents[4] / "labs/search/corpus.json"
    collection = "mlops-local-query"
    s.index_documents("http://unused.invalid:6333", corpus, collection=collection)
    hits = s.query_documents(
        "http://unused.invalid:6333",
        [0, 0, 0, 1],
        k=2,
        topic="security",
        collection=collection,
    )
    assert {hit["id"] for hit in hits} == {7, 8}
    assert all(hit["payload"]["topic"] == "security" for hit in hits)
    by_id = {hit["id"]: hit for hit in hits}
    assert by_id[7]["score"] == pytest.approx(1.0)
    assert by_id[8]["score"] == pytest.approx(0.8 / (0.66**0.5))
    release = s.query_documents(
        "http://unused.invalid:6333",
        [1, 0, 0, 0],
        k=2,
        topic="release",
        collection=collection,
    )
    assert {hit["id"] for hit in release} == {1}
    assert (
        s.query_documents(
            "http://unused.invalid:6333",
            [0, 0, 0, 1],
            topic="missing",
            collection=collection,
        )
        == []
    )
    with pytest.raises(ValueError):
        s.query_documents("http://unused.invalid:6333", [1, 0], collection=collection)


@pytest.mark.integration
@pytest.mark.writes
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_INTEGRATION") != "1" or os.getenv("MLOPS_RUN_WRITES") != "1",
    reason="Set both MLOPS_RUN_INTEGRATION=1 and MLOPS_RUN_WRITES=1",
)
def test_live_student_index_query_and_metrics_use_owned_collection():
    assert QdrantClient is not None, "Install labs/qdrant/requirements.txt"
    url = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
    client = QdrantClient(url=url)
    collection = "mlops-test-qdrant-" + uuid4().hex
    assert not client.collection_exists(collection)
    corpus = Path(__file__).resolve().parents[4] / "labs/search/corpus.json"
    try:
        s.index_documents(url, corpus, collection=collection)
        s.index_documents(url, corpus, collection=collection)
        assert client.count(collection, exact=True).count == 8
        queries = json.loads(corpus.with_name("queries.json").read_text())
        metrics = load_task("13-qdrant/02-evaluation")
        for query in queries:
            hits = s.query_documents(url, query["vector"], k=2, collection=collection)
            assert all(isinstance(hit["score"], (int, float)) for hit in hits)
            assert metrics.ranking_metrics(
                [hit["id"] for hit in hits], query["relevant"], 2
            ) == {"recall": 1.0, "precision": 1.0, "mrr": 1.0}
        hits = s.query_documents(
            url, [0, 0, 0, 1], k=8, topic="security", collection=collection
        )
        assert {hit["id"] for hit in hits} == {7, 8}
        assert all(hit["payload"]["topic"] == "security" for hit in hits)
        assert (
            s.query_documents(url, [0, 0, 0, 1], topic="missing", collection=collection)
            == []
        )
    finally:
        if client.collection_exists(collection):
            client.delete_collection(collection)
        client.close()

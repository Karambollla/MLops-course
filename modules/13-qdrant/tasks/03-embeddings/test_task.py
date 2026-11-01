import hashlib

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_manifest_records_actual_vector_shape_and_corpus_hash():
    result = s.make_manifest(
        "BAAI/bge-small-en-v1.5", "a" * 40, [[1.0, 0.0], [0.0, 1.0]], b"corpus"
    )
    assert result == {
        "model_id": "BAAI/bge-small-en-v1.5",
        "revision": "a" * 40,
        "dimension": 2,
        "count": 2,
        "corpus_sha256": hashlib.sha256(b"corpus").hexdigest(),
    }


@pytest.mark.parametrize(
    "vectors", [[], [[0.0, 0.0]], [[1.0], [1.0, 2.0]], [[float("inf"), 1.0]]]
)
def test_invalid_embedding_output_is_not_indexed(vectors):
    with pytest.raises(ValueError):
        s.make_manifest("model", "a" * 40, vectors, b"corpus")


@pytest.mark.parametrize("revision", ["main", "latest"])
def test_mutable_revision_is_not_reproducible(revision):
    with pytest.raises(ValueError):
        s.make_manifest("model", revision, [[1.0]], b"corpus")


@pytest.mark.parametrize(
    "vectors",
    [
        [[float("nan"), 1]],
        [["x", 1]],
        [[], []],
        [[1, 2], [3]],
        [[1, 2], [float("inf"), 3]],
    ],
)
def test_other_invalid_embedding_values(vectors):
    with pytest.raises(ValueError):
        s.make_manifest("model", "a" * 40, vectors, b"corpus")


def test_manifest_hash_uses_exact_bytes_even_for_equivalent_json():
    first, second = b'{"id":1}', b'{ "id": 1 }'
    a = s.make_manifest("model", "a" * 40, [[1, 2, 3]], first)
    b = s.make_manifest("model", "a" * 40, [[1, 2, 3]], second)
    assert a["dimension"] == b["dimension"] == 3
    assert a["count"] == b["count"] == 1
    assert a["corpus_sha256"] == hashlib.sha256(first).hexdigest()
    assert b["corpus_sha256"] == hashlib.sha256(second).hexdigest()
    assert a["corpus_sha256"] != b["corpus_sha256"]

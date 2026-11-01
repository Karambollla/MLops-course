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

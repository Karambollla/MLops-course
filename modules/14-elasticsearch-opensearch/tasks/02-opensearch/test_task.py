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

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_metrics_match_hand_calculation():
    assert s.ranking_metrics([1, 3], [1, 2], 2) == {
        "recall": 0.5,
        "precision": 0.5,
        "mrr": 1.0,
    }
    result = s.ranking_metrics([9, 2], [1, 2], 2)
    assert result == {"recall": 0.5, "precision": 0.5, "mrr": 0.5}


def test_duplicates_do_not_inflate_relevance_and_cutoff_is_respected():
    assert s.ranking_metrics([1, 1, 2], [1, 2], 2) == {
        "recall": 0.5,
        "precision": 0.5,
        "mrr": 1.0,
    }
    assert s.ranking_metrics([1], [], 2) == {
        "recall": 0.0,
        "precision": 0.0,
        "mrr": 0.0,
    }
    assert s.ranking_metrics([], [1], 2) == {
        "recall": 0.0,
        "precision": 0.0,
        "mrr": 0.0,
    }


@pytest.mark.parametrize("k", [0, -1, True])
def test_invalid_cutoff(k):
    with pytest.raises(ValueError):
        s.ranking_metrics([1], [1], k)


@pytest.mark.parametrize(
    "retrieved,relevant,k,expected",
    [
        ([2, 1], [1, 2], 2, (1, 1, 1)),
        ([8, 9], [1, 2], 2, (0, 0, 0)),
        ([9, 8, 1], [1], 2, (0, 0, 0)),
        ([1], [1, 2], 4, (0.5, 0.25, 1)),
        ([9, 1], [1, 1, 2, 2], 3, (0.5, 1 / 3, 0.5)),
    ],
)
def test_ranking_boundaries_and_unique_qrels(retrieved, relevant, k, expected):
    result = s.ranking_metrics(retrieved, relevant, k)
    assert result == dict(zip(["recall", "precision", "mrr"], expected))

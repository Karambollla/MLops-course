import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_rrf_combines_ranks_with_deterministic_ties():
    result = s.reciprocal_rank_fusion([[1, 2], [2, 1]])
    assert [r["id"] for r in result] == [1, 2]
    assert result[0]["score"] == pytest.approx(1 / 61 + 1 / 62)
    assert result[1]["score"] == pytest.approx(result[0]["score"])


def test_duplicates_do_not_add_the_same_list_twice():
    result = s.reciprocal_rank_fusion([[1, 1, 2], [2]])
    scores = {r["id"]: r["score"] for r in result}
    assert scores[1] == pytest.approx(1 / 61)
    assert scores[2] == pytest.approx(1 / 63 + 1 / 61)
    assert s.reciprocal_rank_fusion([]) == []


def test_negative_constant_is_invalid():
    with pytest.raises(ValueError):
        s.reciprocal_rank_fusion([[1]], constant=-1)

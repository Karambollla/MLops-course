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


def test_empty_lists_and_disjoint_rankings_preserve_first_seen_ties():
    assert s.reciprocal_rank_fusion([[], [], []]) == []
    result = s.reciprocal_rank_fusion([[], [9, 3], [7, 1], []], constant=0)
    assert [row["id"] for row in result] == [9, 7, 3, 1]
    assert [row["score"] for row in result] == pytest.approx([1, 1, 0.5, 0.5])


def test_three_rankings_with_nondefault_constant():
    result = s.reciprocal_rank_fusion([[8, 2], [2, 5], [5, 2, 8]], constant=2)
    assert [row["id"] for row in result] == [2, 5, 8]
    assert [row["score"] for row in result] == pytest.approx(
        [
            1 / 4 + 1 / 3 + 1 / 4,
            1 / 4 + 1 / 3,
            1 / 3 + 1 / 5,
        ]
    )

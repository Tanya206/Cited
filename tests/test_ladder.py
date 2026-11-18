import pytest

from eval.ladder import aggregate, compare, paired_bootstrap_ci, score_lists

ITEM = {"expected_doc_ids": ["paper-a"], "expected_pages": [3]}


def _chunk(doc, page):
    return {"doc_id": doc, "page_number": page}


def test_score_lists_scores_each_k_on_its_own_list():
    lists = {
        6: [_chunk("paper-b", 1)] * 6,
        20: [_chunk("paper-b", 1)] * 9 + [_chunk("paper-a", 3)] + [_chunk("paper-b", 1)] * 10,
    }
    scores = score_lists(lists, ITEM)
    assert scores[6]["page_hit"] is False
    assert scores[20]["first_page_rank"] == 10
    assert scores[20]["page_reciprocal_rank"] == 0.1


def test_aggregate_reports_rates_and_counts():
    rows = [
        {"doc_hit": True, "page_hit": True, "doc_reciprocal_rank": 1.0, "page_reciprocal_rank": 0.5},
        {"doc_hit": True, "page_hit": False, "doc_reciprocal_rank": 0.5, "page_reciprocal_rank": 0.0},
    ]
    assert aggregate(rows) == {
        "n": 2, "doc_hit": 1.0, "page_hit": 0.5, "doc_reciprocal_rank": 0.75,
        "page_reciprocal_rank": 0.25, "doc_hits": 2, "page_hits": 1,
    }


def test_bootstrap_is_deterministic_and_brackets_the_mean():
    before = [0.0, 0.5, 1.0, 0.2, 0.0, 1.0]
    after = [0.5, 0.5, 1.0, 1.0, 0.0, 1.0]
    first = paired_bootstrap_ci(before, after)
    assert first == paired_bootstrap_ci(before, after)
    mean_diff, low, high = first
    assert low <= mean_diff <= high


def test_identical_configs_have_zero_change():
    values = [0.0, 0.5, 1.0]
    assert paired_bootstrap_ci(values, values) == (0.0, 0.0, 0.0)


def test_bootstrap_rejects_unpaired_input():
    with pytest.raises(ValueError):
        paired_bootstrap_ci([1.0], [1.0, 0.0])


def _row(item_id, before_hit, after_hit):
    def score(hit):
        return {"page_hit": hit, "page_reciprocal_rank": 1.0 if hit else 0.0}
    return {"id": item_id, "scores": {"a": {6: score(before_hit)}, "b": {6: score(after_hit)}}}


def test_compare_lists_gained_and_lost_items():
    rows = [_row("G1", False, True), _row("G2", True, False), _row("G3", True, True)]
    result = compare(rows, "a", "b", 6)
    assert result["page_hit_gained"] == ["G1"]
    assert result["page_hit_lost"] == ["G2"]
    assert result["page_mrr_change"] == 0.0


def test_exact_mcnemar_matches_known_binomial_values():
    from eval.ladder import exact_mcnemar_p

    assert exact_mcnemar_p(0, 0) == 1.0
    assert exact_mcnemar_p(3, 3) == 1.0
    # 11 vs 2 discordant: 2 * P(X <= 2 | n=13, p=0.5) = 2 * 92 / 8192
    assert exact_mcnemar_p(11, 2) == round(2 * 92 / 8192, 4)
    assert exact_mcnemar_p(2, 11) == exact_mcnemar_p(11, 2)

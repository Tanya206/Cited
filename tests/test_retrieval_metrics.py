from eval.retrieval_metrics import aggregate, score_query


def test_score_query_measures_doc_and_page_rank():
    results = [
        {"doc_id": "wrong", "page_number": 1},
        {"doc_id": "paper-a", "page_number": 4},
        {"doc_id": "paper-a", "page_number": 2},
    ]
    scored = score_query(results, ["paper-a"], [2], 3)
    assert scored["doc_hit"] is True
    assert scored["page_hit"] is True
    assert scored["doc_reciprocal_rank"] == 0.5
    assert scored["page_reciprocal_rank"] == 1 / 3


def test_aggregate_is_empty_safe():
    assert aggregate([]) == {"count": 0}

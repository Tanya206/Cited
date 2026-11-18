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


def test_v1_scoring_lets_a_page_number_from_the_wrong_paper_count():
    # Two-paper item: SimCLR p3 and MoCo p1. v1 pages are not tied to papers.
    results = [{"doc_id": "simclr", "page_number": 1}]
    scored = score_query(results, ["simclr", "moco"], [1, 3], 1)
    assert scored["page_hit"] is True  # the flaw golden v2 fixes


def test_expected_locations_tie_pages_to_papers():
    locations = [{"doc_id": "simclr", "page_number": 3}, {"doc_id": "moco", "page_number": 1}]
    wrong = score_query([{"doc_id": "simclr", "page_number": 1}], ["simclr", "moco"], [1, 3], 1, locations)
    right = score_query([{"doc_id": "moco", "page_number": 1}], ["simclr", "moco"], [1, 3], 1, locations)
    assert wrong["page_hit"] is False and wrong["doc_hit"] is True
    assert right["page_hit"] is True

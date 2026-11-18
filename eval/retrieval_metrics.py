"""Deterministic retrieval metrics used by local evaluation and CI.

The metrics deliberately do not call an LLM.  A result is relevant when it
retrieves an expected document, and a stronger result when it retrieves the
expected document page.  This makes the regression gate cheap and repeatable.
"""

from collections import defaultdict
from typing import Iterable


def _key(item: dict) -> tuple[str, int]:
    return str(item["doc_id"]), int(item["page_number"])


def score_query(
    results: Iterable[dict],
    expected_doc_ids: list[str],
    expected_pages: list[int],
    k: int,
    expected_locations: list[dict] | None = None,
) -> dict:
    """Score one ranked list.

    Golden v1 gives pages that apply to any expected document, so for a two-paper item a
    page number from the wrong paper still counts. Golden v2 can give ``expected_locations``
    as (doc_id, page) pairs; when present, a page hit must match a pair.
    """
    ranked = list(results)[:k]
    expected_docs = set(expected_doc_ids)
    expected_pages_set = set(expected_pages)
    locations = (
        {(str(loc["doc_id"]), int(loc["page_number"])) for loc in expected_locations}
        if expected_locations else None
    )

    def is_page_hit(item: dict) -> bool:
        doc, page = item.get("doc_id"), int(item.get("page_number", -1))
        if locations is not None:
            return (doc, page) in locations
        return doc in expected_docs and page in expected_pages_set

    doc_ranks = [i for i, item in enumerate(ranked, 1) if item.get("doc_id") in expected_docs]
    page_ranks = [i for i, item in enumerate(ranked, 1) if is_page_hit(item)]
    return {
        "doc_hit": bool(doc_ranks),
        "page_hit": bool(page_ranks),
        "doc_reciprocal_rank": 1 / doc_ranks[0] if doc_ranks else 0.0,
        "page_reciprocal_rank": 1 / page_ranks[0] if page_ranks else 0.0,
        "first_doc_rank": doc_ranks[0] if doc_ranks else None,
        "first_page_rank": page_ranks[0] if page_ranks else None,
    }


def aggregate(rows: list[dict]) -> dict:
    if not rows:
        return {"count": 0}
    numeric = ("doc_hit", "page_hit", "doc_reciprocal_rank", "page_reciprocal_rank")
    return {"count": len(rows), **{name: round(sum(float(row[name]) for row in rows) / len(rows), 4) for name in numeric}}


def aggregate_by_category(rows: list[dict]) -> dict[str, dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[row["category"]].append(row)
    return {category: aggregate(group) for category, group in sorted(groups.items())}

"""Pure helpers for the retrieval comparison ladder (no models, no index; unit-tested)."""

import math
import random
from statistics import mean

from eval.retrieval_metrics import score_query

# The ladder adds one component per step. Every step ranks the same 20-candidate pool size,
# and every step is scored at the same k, so differences come from the component added.
STEPS = (
    ("vector", "Dense only: bge-small-en-v1.5 cosine search in Chroma, raw question"),
    ("bm25", "Lexical only: bm25s with English stemming and stopwords, raw question"),
    ("hybrid", "Reciprocal Rank Fusion (k=10) of the vector and BM25 lists, raw question"),
    ("hybrid_expand", "hybrid with rule-based query expansion (the served retrieval)"),
    ("hybrid_expand_rerank", "hybrid_expand candidates reordered by the MiniLM cross-encoder (served pipeline)"),
)
STEP_NAMES = tuple(name for name, _ in STEPS)
METRICS = ("doc_hit", "page_hit", "doc_reciprocal_rank", "page_reciprocal_rank")


def score_lists(lists_by_k: dict[int, list[dict]], item: dict) -> dict[int, dict]:
    """Score one item's ranked list at each k."""
    return {
        k: score_query(
            ranked, item["expected_doc_ids"], item["expected_pages"], k,
            item.get("expected_locations"),
        )
        for k, ranked in lists_by_k.items()
    }


def aggregate(scores: list[dict]) -> dict:
    """Mean of each metric over items, plus the hit counts behind the rates."""
    n = len(scores)
    if n == 0:
        return {"n": 0}
    summary = {"n": n}
    for metric in METRICS:
        summary[metric] = round(mean(float(score[metric]) for score in scores), 4)
    summary["doc_hits"] = sum(bool(score["doc_hit"]) for score in scores)
    summary["page_hits"] = sum(bool(score["page_hit"]) for score in scores)
    return summary


def paired_bootstrap_ci(
    before: list[float], after: list[float], resamples: int = 10_000, seed: int = 0
) -> tuple[float, float, float]:
    """Mean of (after - before) over the same items, with a 95% percentile bootstrap CI.

    Paired, because both configurations answer the same questions: resampling questions,
    not configurations, is what tells us whether the difference survives a different sample.
    """
    if len(before) != len(after) or not before:
        raise ValueError("paired lists must be non-empty and the same length")
    diffs = [b - a for a, b in zip(before, after)]
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(mean(diffs[rng.randrange(n)] for _ in range(n)) for _ in range(resamples))
    low = means[int(0.025 * resamples)]
    high = means[int(0.975 * resamples) - 1]
    return round(mean(diffs), 4), round(low, 4), round(high, 4)


def exact_mcnemar_p(gained: int, lost: int) -> float:
    """Two-sided exact McNemar test on the items whose page hit changed.

    Items that both configurations got right (or both wrong) carry no information about
    which is better; only the discordant ones do. Under "no difference", each discordant
    item is a fair coin flip, so this is a binomial test with p = 0.5.
    """
    n = gained + lost
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(gained, lost) + 1)) / 2 ** n
    return round(min(1.0, 2 * tail), 4)


def compare(
    per_item: list[dict], before: str, after: str, k: int
) -> dict:
    """Paired comparison of two steps at one k: items gained and lost, and the MRR change."""
    pairs = [(row["scores"][before][k], row["scores"][after][k], row["id"]) for row in per_item]
    gained = [item_id for b, a, item_id in pairs if not b["page_hit"] and a["page_hit"]]
    lost = [item_id for b, a, item_id in pairs if b["page_hit"] and not a["page_hit"]]
    mrr_diff, low, high = paired_bootstrap_ci(
        [b["page_reciprocal_rank"] for b, _, _ in pairs],
        [a["page_reciprocal_rank"] for _, a, _ in pairs],
    )
    return {
        "before": before,
        "after": after,
        "k": k,
        "page_hit_gained": gained,
        "page_hit_lost": lost,
        "page_hit_mcnemar_p": exact_mcnemar_p(len(gained), len(lost)),
        "page_mrr_change": mrr_diff,
        "page_mrr_change_ci95": [low, high],
        "ci_excludes_zero": low > 0 or high < 0,
    }

"""Retrieval comparison ladder: what each component adds, measured on the same questions.

No LLM calls. Loads the local Chroma and BM25 indexes and the embedding and reranker models
(already cached), runs every answerable golden item through five configurations, and scores
each at k=6 (what the generator sees) and k=20 (the candidate pool).

    python -m eval.run_ladder
"""

import argparse
import json
import platform
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from app.core import reranker as reranker_module
from app.core.bm25_index import bm25_search, load_index
from app.core.reranker import Reranker
from app.core.retrieval import (
    BM25_INDEX_DIR, CHROMA_PATH, COLLECTION_NAME, MODEL_NAME, hybrid_retrieve, vector_search,
)
from eval.golden import GOLDEN_V1, answerable_items, content_sha256
from eval.ladder import STEP_NAMES, STEPS, aggregate, compare, score_lists

POOL = 20          # candidates per retriever and size of every ranked list (as served)
KS = (6, 20)       # 6 = what the generator sees after rerank; 20 = the candidate pool
RRF_K = 10         # as served (app/core/retrieval.py)

# Comparisons reported: each step against the one before it, plus the served pipeline
# against the strongest single retriever.
COMPARISONS = [
    ("vector", "bm25"),
    ("vector", "hybrid"),
    ("bm25", "hybrid"),
    ("hybrid", "hybrid_expand"),
    ("hybrid_expand", "hybrid_expand_rerank"),
]


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout.strip()


def ranked_lists(question, collection, embed_model, bm25, chunk_map, reranker) -> dict[str, dict[int, list]]:
    """Every step's ranked list for one question, keyed by step then k."""
    vector = vector_search(collection, embed_model, question, k=POOL)
    lexical = bm25_search(bm25, chunk_map, question, k=POOL)
    common = dict(k_per_retriever=POOL, k_final=POOL, rrf_k=RRF_K)
    hybrid = hybrid_retrieve(question, collection, embed_model, bm25, chunk_map, expand=False, **common)
    expanded = hybrid_retrieve(question, collection, embed_model, bm25, chunk_map, expand=True, **common)
    lists = {
        "vector": {k: vector[:k] for k in KS},
        "bm25": {k: lexical[:k] for k in KS},
        "hybrid": {k: hybrid[:k] for k in KS},
        "hybrid_expand": {k: expanded[:k] for k in KS},
        # The served reranker is called with top_k directly: its table-promotion rule depends
        # on top_k, so k=6 is not simply the first 6 of a top-20 rerank.
        "hybrid_expand_rerank": {k: reranker.rerank(question, expanded, k) for k in KS},
    }
    return lists


def check_against_baseline(per_item: list[dict], baseline_path: Path) -> dict:
    """Recompute the saved 2026-11-12 baseline: hybrid_expand@20 and rerank@6, item by item."""
    baseline = {row["id"]: row for row in json.loads(baseline_path.read_text(encoding="utf-8"))["items"]}
    mismatches = []
    for row in per_item:
        saved = baseline.get(row["id"])
        if saved is None:
            mismatches.append({"id": row["id"], "reason": "missing from baseline"})
            continue
        now_hybrid = row["scores"]["hybrid_expand"][20]
        now_rerank = row["scores"]["hybrid_expand_rerank"][6]
        for label, now, then in (("hybrid_expand@20", now_hybrid, saved), ("rerank@6", now_rerank, saved["reranked"])):
            if (now["first_doc_rank"], now["first_page_rank"]) != (then["first_doc_rank"], then["first_page_rank"]):
                mismatches.append({
                    "id": row["id"], "config": label,
                    "now": [now["first_doc_rank"], now["first_page_rank"]],
                    "baseline": [then["first_doc_rank"], then["first_page_rank"]],
                })
    return {"baseline_file": str(baseline_path), "items_compared": len(per_item), "mismatches": mismatches}


def markdown_summary(report: dict) -> str:
    meta = report["meta"]
    lines = [
        f"# Retrieval comparison ladder, golden v1 ({meta['date']})",
        "",
        f"n={meta['n_items']} answerable items; pool {POOL} per retriever; RRF k={RRF_K}; "
        f"commit {meta['commit']}; no LLM calls.",
        "",
        "| Step | k | doc hit | page hit | doc MRR | page MRR |",
        "|---|---|---|---|---|---|",
    ]
    for step in STEP_NAMES:
        for k in KS:
            agg = report["overall"][step][str(k)]
            lines.append(
                f"| {step} | {k} | {agg['doc_hit']:.3f} ({agg['doc_hits']}/{agg['n']}) | "
                f"{agg['page_hit']:.3f} ({agg['page_hits']}/{agg['n']}) | "
                f"{agg['doc_reciprocal_rank']:.3f} | {agg['page_reciprocal_rank']:.3f} |"
            )
    lines += ["", "## Paired comparisons (page level)", "",
              "| Before -> after | k | page hits gained | lost | page MRR change [95% CI] |",
              "|---|---|---|---|---|"]
    for comparison in report["comparisons"]:
        low, high = comparison["page_mrr_change_ci95"]
        lines.append(
            f"| {comparison['before']} -> {comparison['after']} | {comparison['k']} | "
            f"{len(comparison['page_hit_gained'])} | {len(comparison['page_hit_lost'])} | "
            f"{comparison['page_mrr_change']:+.3f} [{low:+.3f}, {high:+.3f}] |"
        )
    lines += ["", "Categories with n <= 3 are in the JSON but not quoted here.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=GOLDEN_V1)
    parser.add_argument("--out-dir", type=Path, default=Path("eval/results"))
    parser.add_argument("--baseline", type=Path, default=Path("eval/baseline_before_docling.json"))
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    items = answerable_items(dataset)
    collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(name=COLLECTION_NAME)
    embed_model = SentenceTransformer(MODEL_NAME)
    bm25, chunk_map = load_index(BM25_INDEX_DIR)
    reranker = Reranker()

    per_item = []
    for item in items:
        lists = ranked_lists(item["question"], collection, embed_model, bm25, chunk_map, reranker)
        per_item.append({
            "id": item["id"],
            "category": item["category"],
            "scores": {step: score_lists(lists[step], item) for step in STEP_NAMES},
        })

    overall = {step: {str(k): aggregate([row["scores"][step][k] for row in per_item]) for k in KS} for step in STEP_NAMES}
    by_category: dict = defaultdict(dict)
    for category in sorted({row["category"] for row in per_item}):
        rows = [row for row in per_item if row["category"] == category]
        for step in STEP_NAMES:
            by_category[category][step] = {str(k): aggregate([row["scores"][step][k] for row in rows]) for k in KS}
    comparisons = [compare(per_item, before, after, k) for before, after in COMPARISONS for k in KS]

    today = date.today().isoformat()
    report = {
        "meta": {
            "date": today,
            "commit": _git("rev-parse", "--short", "HEAD"),
            "uncommitted_changes": bool(_git("status", "--porcelain", "--untracked-files=no")),
            "dataset": str(args.dataset).replace("\\", "/"),
            "dataset_sha256": content_sha256(args.dataset),
            "n_items": len(per_item),
            "ks": list(KS),
            "pool_per_retriever": POOL,
            "rrf_k": RRF_K,
            "embedding_model": MODEL_NAME,
            "reranker_model": reranker_module.MODEL_NAME,
            "index": {
                "chunks": collection.count(),
                "chunks_jsonl_mtime": Path("data/chunks.jsonl").stat().st_mtime,
            },
            "python": platform.python_version(),
            "llm_calls": 0,
            "steps": dict(STEPS),
        },
        "overall": overall,
        "by_category": by_category,
        "comparisons": comparisons,
        "baseline_check": check_against_baseline(per_item, args.baseline) if args.baseline.exists() else None,
        "items": [
            {**row, "scores": {s: {str(k): v for k, v in by_k.items()} for s, by_k in row["scores"].items()}}
            for row in per_item
        ],
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"ladder_{args.dataset.stem}_{today}"
    (args.out_dir / f"{stem}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = markdown_summary(report)
    (args.out_dir / f"{stem}.md").write_text(summary, encoding="utf-8")
    print(summary)
    check = report["baseline_check"]
    if check is not None:
        print(f"Baseline check: {check['items_compared']} items, {len(check['mismatches'])} mismatches")


if __name__ == "__main__":
    main()

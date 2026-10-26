"""Run the full-corpus retrieval baseline.

This command loads the existing local indexes, evaluates answerable golden
questions, and writes a JSON report.  It never calls Groq or Ragas.
"""

import argparse
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.bm25_index import load_index
from app.core.reranker import Reranker
from app.core.retrieval import BM25_INDEX_DIR, CHROMA_PATH, COLLECTION_NAME, MODEL_NAME, hybrid_retrieve
from eval.retrieval_metrics import aggregate, aggregate_by_category, score_query


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("eval/golden_dataset.json"))
    parser.add_argument("--out", type=Path, default=Path("eval/baseline_retrieval.json"))
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument("--rerank", action="store_true", help="Also report reranked page metrics.")
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    model = SentenceTransformer(MODEL_NAME)
    bm25, chunk_map = load_index(BM25_INDEX_DIR)
    reranker = Reranker() if args.rerank else None

    rows = []
    for item in dataset["items"]:
        if item.get("expects_refusal") or item.get("expected_outcome", "answer") != "answer":
            continue
        retrieved = hybrid_retrieve(item["question"], collection, model, bm25, chunk_map, k_per_retriever=args.k, k_final=args.k)
        result = score_query(retrieved, item["expected_doc_ids"], item["expected_pages"], args.k)
        if reranker:
            reranked = reranker.rerank(item["question"], retrieved, min(6, args.k))
            result["reranked"] = score_query(reranked, item["expected_doc_ids"], item["expected_pages"], len(reranked))
        rows.append({"id": item["id"], "category": item["category"], **result})

    report = {"dataset": str(args.dataset), "k": args.k, "overall": aggregate(rows), "by_category": aggregate_by_category(rows), "items": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"items": len(rows), "overall": report["overall"], "by_category": report["by_category"]}, indent=2))


if __name__ == "__main__":
    main()

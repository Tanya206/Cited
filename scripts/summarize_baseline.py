import json

report = json.load(open("eval/baseline_before_docling.json", encoding="utf-8"))
keys = ("doc_hit", "page_hit", "doc_reciprocal_rank", "page_reciprocal_rank")

reranked = [item["reranked"] for item in report["items"] if "reranked" in item]
print("reranked @6:", {k: round(sum(float(r[k]) for r in reranked) / len(reranked), 4) for k in keys})

print("\npage misses (before reranking):")
for item in report["items"]:
    if not item["page_hit"]:
        print(" ", item["id"], item["category"])
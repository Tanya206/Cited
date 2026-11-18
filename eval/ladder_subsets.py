"""Subset views of a ladder result: table questions, expansion triggers, named vs unnamed pairs.

Reads a ladder JSON written by eval/run_ladder.py plus the golden file it was run on. No models.

    python -m eval.ladder_subsets eval/results/ladder_golden_v2_2026-11-19.json
"""

import argparse
import json
from pathlib import Path

from eval.ladder import STEP_NAMES, aggregate

TABLE_CATEGORIES = ("numeric_table", "numeric_table_text")
SERVED = "hybrid_expand_rerank"


def subset_table(rows: list[dict], ks=("6", "20")) -> dict:
    return {step: {k: aggregate([row["scores"][step][k] for row in rows]) for k in ks} for step in STEP_NAMES}


def named_vs_unnamed(rows_by_id: dict, items: list[dict], step: str = SERVED, k: str = "6") -> list[dict]:
    pairs = []
    for item in items:
        original = item.get("variant_of")
        if not original or item["id"] not in rows_by_id or original not in rows_by_id:
            continue
        unnamed = rows_by_id[item["id"]]["scores"][step][k]
        named = rows_by_id[original]["scores"][step][k]
        pairs.append({
            "unnamed": item["id"], "named": original,
            "named_first_doc_rank": named["first_doc_rank"], "unnamed_first_doc_rank": unnamed["first_doc_rank"],
            "named_page_hit": named["page_hit"], "unnamed_page_hit": unnamed["page_hit"],
        })
    return pairs


def _line(name: str, agg: dict) -> str:
    return (f"| {name} | {agg['page_hits']}/{agg['n']} ({agg['page_hit']:.3f}) | {agg['doc_hits']}/{agg['n']} | "
            f"{agg['page_reciprocal_rank']:.3f} |")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ladder_json", type=Path)
    args = parser.parse_args()
    report = json.loads(args.ladder_json.read_text(encoding="utf-8"))
    dataset = json.loads(Path(report["meta"]["dataset"]).read_text(encoding="utf-8"))
    items = dataset["items"]
    category = {item["id"]: item["category"] for item in items}
    rows_by_id = {row["id"]: row for row in report["items"]}

    lines = [f"# Ladder subsets: {Path(report['meta']['dataset']).stem}, commit {report['meta']['commit']}", ""]
    table_rows = [row for row in report["items"] if category.get(row["id"]) in TABLE_CATEGORIES]
    for title, rows in (("Table questions (structured and body-text)", table_rows),
                        ("Structured table chunks only", [r for r in table_rows if category[r["id"]] == "numeric_table"]),
                        ("Table values only in body/caption text", [r for r in table_rows if category[r["id"]] == "numeric_table_text"])):
        lines += [f"## {title}", "", "| Step @6 | page hit | doc hit | page MRR |", "|---|---|---|---|"]
        lines += [_line(step, subset_table(rows)[step]["6"]) for step in STEP_NAMES] + [""]

    expanded = report["meta"]["questions_changed_by_expansion"]
    lines += ["## Questions changed by query expansion (first labelled page rank @20)", "",
              "| Item | hybrid | hybrid_expand |", "|---|---|---|"]
    for item_id in expanded:
        scores = rows_by_id[item_id]["scores"]
        lines.append(f"| {item_id} | {scores['hybrid']['20']['first_page_rank']} | {scores['hybrid_expand']['20']['first_page_rank']} |")

    pairs = named_vs_unnamed(rows_by_id, items)
    lines += ["", f"## Named vs unnamed paraphrase ({SERVED} @6)", "",
              "| Named item | first doc rank | page hit | Unnamed item | first doc rank | page hit |",
              "|---|---|---|---|---|---|"]
    for pair in pairs:
        lines.append(f"| {pair['named']} | {pair['named_first_doc_rank']} | {pair['named_page_hit']} | "
                     f"{pair['unnamed']} | {pair['unnamed_first_doc_rank']} | {pair['unnamed_page_hit']} |")
    lines += ["", "Small subsets: read these as case studies, not rates.", ""]

    out = args.ladder_json.with_name(args.ladder_json.stem.replace("ladder_", "ladder_subsets_") + ".md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

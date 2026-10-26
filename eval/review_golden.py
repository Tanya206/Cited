"""Print candidate chunks for manually verifying one golden-dataset item."""

import argparse
import json
import sys
from pathlib import Path

from app.core.text_utils import match_key, normalize

def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("item_id", help="Golden item ID, for example G01")
    parser.add_argument("--dataset", type=Path, default=Path("eval/golden_dataset.json"))
    parser.add_argument("--chunks", type=Path, default=Path("data/chunks.jsonl"))
    parser.add_argument("--max-chars", type=int, default=2500)
    parser.add_argument(
        "--grep",
        help="Search all indexed pages of the expected papers for this text.",
    )
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    item = next((entry for entry in dataset["items"] if entry["id"] == args.item_id), None)
    if item is None:
        raise SystemExit(f"Unknown item ID: {args.item_id}")

    print(f"{item['id']} [{item['category']}]\nQ: {item['question']}\nA: {item['reference_answer']}")
    if item["expects_refusal"]:
        print("\nThis is an abstention/clarification case and needs no paper evidence.")
        return

    candidates = [chunk for chunk in load_jsonl(args.chunks) if chunk["doc_id"] in item["expected_doc_ids"]]
    if args.grep:
        # Match on the same hyphenation-tolerant key the validator uses, so a
        # phrase the PDF wrapped across a line break is still findable.
        needle = match_key(args.grep)
        candidates = [chunk for chunk in candidates if needle in match_key(chunk["text"])]
    else:
        candidates = [chunk for chunk in candidates if chunk["page_number"] in item["expected_pages"]]
    print(f"\nCandidate chunks: {len(candidates)}")
    for chunk in candidates:
        excerpt = normalize(chunk["text"])[: args.max_chars]
        print(
            f"\n[{chunk['chunk_id']}] {chunk['doc_id']} p.{chunk['page_number']} "
            f"({chunk['chunk_type']})\n{excerpt}"
        )


if __name__ == "__main__":
    main()

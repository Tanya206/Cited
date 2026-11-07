"""Validate golden-dataset provenance against the indexed JSONL chunks."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from app.core.text_utils import match_key

def load_chunks(path: Path) -> dict[str, dict]:
    chunks: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        chunk = json.loads(line)
        chunks[chunk["chunk_id"]] = chunk
    return chunks


def validate(dataset_path: Path, chunks_path: Path, strict: bool) -> int:
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    chunks = load_chunks(chunks_path)
    pages_by_doc: dict[str, set[int]] = defaultdict(set)
    chunks_by_page: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for chunk in chunks.values():
        pages_by_doc[chunk["doc_id"]].add(chunk["page_number"])
        chunks_by_page[(chunk["doc_id"], chunk["page_number"])].append(chunk)

    errors: list[str] = []
    pending = 0
    seen_ids: set[str] = set()
    for item in dataset["items"]:
        item_id = item["id"]
        if item_id in seen_ids:
            errors.append(f"{item_id}: duplicate ID")
        seen_ids.add(item_id)

        if item["expects_refusal"]:
            if item.get("expected_outcome") not in {"refusal", "clarification"}:
                errors.append(f"{item_id}: refusal item needs expected_outcome")
        elif not item["expected_doc_ids"]:
            errors.append(f"{item_id}: answerable item has no expected_doc_ids")

        for doc_id in item["expected_doc_ids"]:
            if doc_id not in pages_by_doc:
                errors.append(f'{item_id}: unknown doc_id "{doc_id}"')
                continue
            for page in item["expected_pages"]:
                if page not in pages_by_doc[doc_id]:
                    errors.append(f"{item_id}: {doc_id} has no indexed chunk on page {page}")

        evidence = item.get("evidence", [])
        if not item["expects_refusal"] and not evidence:
            pending += 1
            continue
        evidence_docs: set[str] = set()
        required_numbers = item.get("required_numbers", [])
        if required_numbers and not isinstance(required_numbers, list):
            errors.append(f"{item_id}: required_numbers must be a list")
        for source in evidence:
            doc_id = source.get("doc_id")
            page_number = source.get("page_number")
            evidence_docs.add(doc_id)
            if doc_id not in item["expected_doc_ids"]:
                errors.append(f"{item_id}: evidence doc is not expected: {doc_id}")
            if page_number not in item["expected_pages"]:
                errors.append(f"{item_id}: evidence page is not expected: {page_number}")
            quote = match_key(source.get("quote", ""))
            hits = [
                chunk for chunk in chunks_by_page.get((doc_id, page_number), [])
                if quote and quote in match_key(chunk["text"])
            ]
            if not hits:
                errors.append(f"{item_id}: quote not found on {doc_id} p.{page_number}")
        if required_numbers:
            evidence_text = " ".join(source.get("quote", "") for source in evidence)
            normalized_evidence = match_key(evidence_text)
            missing_numbers = [
                number for number in required_numbers
                if match_key(str(number)) not in normalized_evidence
            ]
            if missing_numbers:
                errors.append(f"{item_id}: required numbers missing from evidence: {missing_numbers}")
        if evidence:
            missing_docs = set(item["expected_doc_ids"]) - evidence_docs
            if missing_docs:
                errors.append(f"{item_id}: no evidence for {sorted(missing_docs)}")

    for error in errors:
        print(f"ERROR: {error}")
    print(f"Items: {len(dataset['items'])}; structural errors: {len(errors)}; pending evidence review: {pending}")
    return 1 if errors or (strict and pending) else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("eval/golden_dataset.json"))
    parser.add_argument("--chunks", type=Path, default=Path("data/chunks.jsonl"))
    parser.add_argument("--strict", action="store_true", help="Fail until all answerable items contain verified evidence.")
    args = parser.parse_args()
    raise SystemExit(validate(args.dataset, args.chunks, args.strict))

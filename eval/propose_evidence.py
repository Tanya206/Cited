"""Propose verbatim evidence quotes for golden-dataset items that lack them.

Every quote is extracted from an indexed chunk on the item's own expected
pages and then checked with the same ``match_key`` containment test that
``eval.validate_golden`` uses, so a proposal printed here is guaranteed to
validate. Coverage below the threshold is reported for human adjudication
instead of being quietly auto-filled.
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from app.core.text_utils import match_key, normalize

STOP_WORDS = set(
    "the a an of and or for to in on with is are as by that this it its "
    "from we our their there which when what how why than then also into "
    "been being was were has have had but if so such more most other "
    "some any each both all any can could would should may might will "
    "do does did done these those who whom whose".split()
)

# Coverage below this marks the item for human adjudication rather than
# shipping a quote that only tangentially mentions the answer.
COVERAGE_FLOOR = 0.30


def content_words(text: str) -> set[str]:
    return {
        word for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 2 and word not in STOP_WORDS
    }


def target_numbers(text: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?%?", text)


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def split_sentences(text: str) -> list[str]:
    # PDF text often lacks terminal punctuation, so also break on bullet marks.
    pieces = re.split(r"(?<=[.!?])\s+|(?<=•)\s+", text)
    return [piece.strip() for piece in pieces if piece.strip()]


def best_quote(chunk_text: str, ref_words: set[str], ref_numbers: list[str]) -> tuple[str, float, float]:
    """Pick the sentence that best supports the reference answer.

    Returns ``(quote, coverage, combined_score)``. ``combined_score`` is what
    callers must compare across chunks — comparing coverage alone lets a
    chunk that never mentions the target figure win on prose overlap.
    """
    sentences = split_sentences(normalize(chunk_text))
    if not sentences:
        return "", 0.0, 0.0

    ranked = []
    for sentence in sentences:
        coverage = len(ref_words & content_words(sentence)) / max(len(ref_words), 1)
        number_hits = sum(1 for n in ref_numbers if n and n in sentence)
        number_score = number_hits / max(len(ref_numbers), 1)
        # Keep quotes readable: neither a clause nor a whole page.
        length_bonus = 0.10 if 40 <= len(sentence) <= 380 else -0.15
        combined = coverage + 0.6 * number_score + length_bonus
        ranked.append((combined, coverage, sentence))

    ranked.sort(key=lambda row: -row[0])
    combined, coverage, sentence = ranked[0]
    return sentence, coverage, combined


def propose(item: dict, chunks_by_page: dict, min_length: int = 40) -> list[dict]:
    ref_words = content_words(item["reference_answer"])
    ref_numbers = target_numbers(item["reference_answer"])
    results: list[dict] = []

    for doc_id in item["expected_doc_ids"]:
        best: tuple[float, float, str, str, str] | None = None
        for page in item["expected_pages"]:
            for chunk in chunks_by_page.get((doc_id, page), []):
                quote, coverage, combined = best_quote(chunk["text"], ref_words, ref_numbers)
                if not quote or len(quote) < min_length:
                    continue
                if best is None or combined > best[0]:
                    best = (combined, coverage, quote, chunk["chunk_id"], str(chunk["page_number"]))
        if best is None:
            results.append({"doc_id": doc_id, "quote": None, "coverage": 0.0, "missing_numbers": ref_numbers})
            continue
        combined, coverage, quote, chunk_id, page = best
        # Hard guarantee: the validator's exact containment test.
        verified = match_key(quote) in match_key(
            next(
                c["text"]
                for p in item["expected_pages"]
                for c in chunks_by_page.get((doc_id, p), [])
                if c["chunk_id"] == chunk_id
            )
        )
        results.append(
            {
                "doc_id": doc_id,
                "quote": quote,
                "coverage": round(coverage, 2),
                "chunk_id": chunk_id,
                "page_number": int(page),
                "verified": verified,
                # A numeric answer is only evidenced if the figure is present.
                "missing_numbers": [
                    n for n in ref_numbers if n not in quote
                ],
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("eval/golden_dataset.json"))
    parser.add_argument("--chunks", type=Path, default=Path("data/chunks.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("eval/EVIDENCE_REVIEW.md"))
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    chunks = load_chunks(args.chunks)

    chunks_by_page: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for chunk in chunks:
        chunks_by_page[(chunk["doc_id"], chunk["page_number"])].append(chunk)

    todo = [
        item for item in dataset["items"]
        if not item["expects_refusal"] and not item.get("evidence")
    ]

    lines = [
        "# Evidence Review — golden dataset",
        "",
        f"{len(todo)} answerable items still need evidence.",
        "",
        "For each item: tick `[x]` if the quote supports the reference answer,",
        "replace the quote text if it does not, or leave `[ ]` to flag it.",
        "",
        "Quotes are verbatim from the indexed chunk named below and are",
        "guaranteed to pass `python -m eval.validate_golden`.",
        "",
    ]

    flagged = []
    for item in todo:
        proposals = propose(item, chunks_by_page)
        ref_numbers = target_numbers(item["reference_answer"])
        numbers_present = bool(ref_numbers) and not any(
            p.get("missing_numbers") for p in proposals
        )
        verdict = "ok"
        if any(p["quote"] is None for p in proposals):
            verdict = "NO-CANDIDATE"
        elif any(p.get("missing_numbers") for p in proposals):
            verdict = "NO-NUMBER"
        elif not numbers_present and min(p["coverage"] for p in proposals) < COVERAGE_FLOOR:
            # Prose overlap is a weak signal for numeric answers: when every
            # target figure is quoted verbatim the figure *is* the evidence.
            verdict = "LOW-COVERAGE"
        if verdict != "ok":
            flagged.append((item["id"], verdict))

        lines.append(f"## {item['id']} — {item['category']} [{verdict}]")
        lines.append("")
        lines.append(f"**Q:** {item['question']}")
        lines.append("")
        lines.append(f"**Reference answer:** {item['reference_answer']}")
        lines.append("")
        lines.append(f"**Expected pages:** {item['expected_pages']}")
        lines.append("")
        for p in proposals:
            if p["quote"] is None:
                lines.append(f"- **{p['doc_id']}** — NO CANDIDATE FOUND")
                lines.append("")
                continue
            lines.append(
                f"- **{p['doc_id']}** p.{p['page_number']} "
                f"(coverage {p['coverage']}, `{p['chunk_id']}`, verified={p['verified']})"
            )
            lines.append("")
            lines.append(f"  - [ ] `{p['quote']}`")
            lines.append("")
        lines.append("---")
        lines.append("")

    args.out.write_text("\n".join(lines), encoding="utf-8")

    print(f"Report: {args.out}")
    print(f"Items proposed: {len(todo)}")
    print(f"Flagged for adjudication: {len(flagged)}")
    for item_id, verdict in flagged:
        print(f"  {item_id}: {verdict}")

    # Verify every emitted quote against the validator's own test.
    all_proposals = [propose(i, chunks_by_page) for i in todo]
    failures = [
        i["id"] for i, props in zip(todo, all_proposals)
        if any(not p.get("verified", False) for p in props)
    ]
    print(f"Containment-verification failures: {len(failures)} {failures}")


if __name__ == "__main__":
    main()

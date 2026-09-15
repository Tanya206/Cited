"""
Element-aware chunking for Cited.

Consumes the structured extraction JSON, not flat text. Body text gets
recursive token-based splitting; tables and captions each become exactly
one chunk (never split). Suspicious tables (flagged as unreliable during
extraction) are excluded from embeddable chunks entirely — preserved in
the source JSON and crop for manual inspection, but never cited as
answer evidence.
"""

import os
import json
from transformers import AutoTokenizer
from langchain_text_splitters import RecursiveCharacterTextSplitter

TOKENIZER = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")

CHUNK_SIZE_TOKENS = 400
CHUNK_OVERLAP_TOKENS = 70  # ~17% of chunk size, within bge-small's 512-token limit


def token_len(text: str) -> int:
    """Count real tokens using the embedding model's own tokenizer —
    not characters, since that's what the 512-token limit is measured in."""
    return len(TOKENIZER.encode(text, add_special_tokens=False))


def chunk_body_text(page_text: str, doc_id: str, page_number: int, start_idx: int) -> tuple[list[dict], int]:
    """Recursive token-aware splitting for ordinary body text."""
    if not page_text.strip():
        return [], start_idx

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE_TOKENS,
        chunk_overlap=CHUNK_OVERLAP_TOKENS,
        length_function=token_len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    idx = start_idx
    for chunk_text in splitter.split_text(page_text):
        chunks.append({
            "chunk_id": f"{doc_id}_c{idx:04d}",
            "doc_id": doc_id,
            "page_number": page_number,
            "chunk_type": "body_text",
            "text": chunk_text,
            "token_count": token_len(chunk_text),
        })
        idx += 1
    return chunks, idx


def split_large_table(markdown: str, max_tokens: int = 480) -> list[str]:
    """Split a table's markdown by rows, repeating the header + separator
    row in every piece, so each piece stays independently readable and
    citable without truncation. A single row wider than max_tokens can
    still produce an oversized piece — the downstream oversized-chunk
    filter in chunk_all catches that rare case, so no special handling
    is needed here."""
    lines = markdown.split("\n")
    header, separator, rows = lines[0], lines[1], lines[2:]

    pieces, current = [], [header, separator]
    for row in rows:
        candidate = "\n".join(current + [row])
        if token_len(candidate) > max_tokens and len(current) > 2:
            pieces.append("\n".join(current))
            current = [header, separator, row]
        else:
            current.append(row)
    pieces.append("\n".join(current))
    return pieces


def chunk_tables(tables: list[dict], doc_id: str, page_number: int, start_idx: int) -> tuple[list[dict], int, int]:
    """One chunk per confident table, split into row-based pieces if it
    exceeds the embedding limit. Suspicious tables are skipped entirely —
    not embedded, not citable — per the reliability policy."""
    chunks = []
    idx = start_idx
    skipped = 0

    for table in tables:
        if table["is_suspicious"]:
            skipped += 1
            continue

        full_token_count = token_len(table["markdown"])

        if full_token_count <= 512:
            pieces = [table["markdown"]]
        else:
            pieces = split_large_table(table["markdown"])

        for part_num, piece_text in enumerate(pieces, start=1):
            chunks.append({
                "chunk_id": f"{doc_id}_c{idx:04d}",
                "doc_id": doc_id,
                "page_number": page_number,
                "chunk_type": "table",
                "text": piece_text,
                "token_count": token_len(piece_text),
                "source_image_path": table["source_image_path"],
                "empty_cell_ratio": table["empty_cell_ratio"],
                "table_part": part_num,
                "table_part_total": len(pieces),
            })
            idx += 1

    return chunks, idx, skipped
def chunk_captions(captions: list[dict], doc_id: str, page_number: int, start_idx: int) -> tuple[list[dict], int]:
    """One chunk per caption."""
    chunks = []
    idx = start_idx
    for caption in captions:
        chunks.append({
            "chunk_id": f"{doc_id}_c{idx:04d}",
            "doc_id": doc_id,
            "page_number": page_number,
            "chunk_type": "caption",
            "text": caption["text"],
            "token_count": token_len(caption["text"]),
            "refers_to": caption["refers_to"],
            "number": caption["number"],
        })
        idx += 1
    return chunks, idx


def chunk_document(structured_path: str) -> tuple[list[dict], int]:
    """Chunk one paper's structured JSON into embeddable chunks.
    Returns (chunks, suspicious_tables_skipped)."""
    with open(structured_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    doc_id = doc["doc_id"]
    all_chunks = []
    idx = 0
    total_skipped = 0

    for page in doc["pages"]:
        page_number = page["page_number"]

        body_chunks, idx = chunk_body_text(page["body_text"], doc_id, page_number, idx)
        all_chunks.extend(body_chunks)

        table_chunks, idx, skipped = chunk_tables(page["tables"], doc_id, page_number, idx)
        all_chunks.extend(table_chunks)
        total_skipped += skipped

        caption_chunks, idx = chunk_captions(page["captions"], doc_id, page_number, idx)
        all_chunks.extend(caption_chunks)

    return all_chunks, total_skipped


def chunk_all(structured_dir: str, output_path: str) -> None:
    """Chunk every paper, write all chunks to one JSONL file, print a
    per-type summary for a sanity check before embedding."""
    all_chunks = []
    total_skipped = 0
    files = [f for f in os.listdir(structured_dir) if f.endswith(".json")]

    for fname in sorted(files):
        path = os.path.join(structured_dir, fname)
        chunks, skipped = chunk_document(path)
        all_chunks.extend(chunks)
        total_skipped += skipped
        print(f"{fname[:-5]}: {len(chunks)} chunks ({skipped} suspicious tables skipped)")

    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")

    by_type = {}
    for c in all_chunks:
        by_type[c["chunk_type"]] = by_type.get(c["chunk_type"], 0) + 1

    over_limit = [c for c in all_chunks if c["token_count"] > 512]

    print(f"\nTotal: {len(all_chunks)} chunks across {len(files)} papers")
    print(f"By type: {by_type}")
    print(f"Suspicious tables skipped (not embedded): {total_skipped}")
    if over_limit:
        print(f"⚠ {len(over_limit)} chunks exceed the 512-token embedding limit — check these before embedding")
        for c in over_limit[:5]:
            print(f"  {c['chunk_id']} ({c['chunk_type']}): {c['token_count']} tokens")


if __name__ == "__main__":
    chunk_all("data/extracted_structured", "data/chunks.jsonl")

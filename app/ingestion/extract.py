"""
PDF extraction for the Cited corpus.

Handles: multi-column vs single-column layout detection, control-character
cleanup from older PDFs' broken font encodings, and a post-extraction
sanity check to flag files that likely failed silently.
"""

import os
import fitz  # PyMuPDF


def extract_ordered_text(pdf_path: str, out_path: str) -> None:
    """Extract text from a PDF in correct reading order, handling both
    single- and multi-column layouts, and strip unprintable control
    characters left over from older PDFs' font encoding issues."""
    doc = fitz.open(pdf_path)
    with open(out_path, "w", encoding="utf-8") as f:
        for page in doc:
            blocks = page.get_text("blocks")
            page_width = page.rect.width
            mid_x = page_width / 2

            wide_blocks = [b for b in blocks if (b[2] - b[0]) > 0.6 * page_width]
            is_single_column = len(wide_blocks) > len(blocks) * 0.5

            if is_single_column:
                ordered = sorted(blocks, key=lambda b: b[1])
            else:
                left = sorted([b for b in blocks if b[0] < mid_x], key=lambda b: b[1])
                right = sorted([b for b in blocks if b[0] >= mid_x], key=lambda b: b[1])
                ordered = left + right

            for b in ordered:
                cleaned = "".join(ch for ch in b[4] if ch == "\n" or ord(ch) >= 0x20)
                f.write(cleaned + "\n")


def extract_all(raw_dir: str, extracted_dir: str) -> list[str]:
    """Run extraction over every PDF in raw_dir. Returns a list of
    filenames that failed, instead of letting one bad file kill the batch."""
    os.makedirs(extracted_dir, exist_ok=True)
    failures = []
    for pdf_file in os.listdir(raw_dir):
        if not pdf_file.lower().endswith(".pdf"):
            continue
        try:
            extract_ordered_text(
                os.path.join(raw_dir, pdf_file),
                os.path.join(extracted_dir, pdf_file + ".txt"),
            )
        except Exception as e:
            failures.append(f"{pdf_file} — {e}")
    return failures


def sanity_check(extracted_dir: str) -> list[tuple[str, int, str]]:
    """Flag likely-broken extractions: too short, missing a references
    section, or a high ratio of leftover garbled characters."""
    results = []
    for fname in os.listdir(extracted_dir):
        path = os.path.join(extracted_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        word_count = len(text.split())
        has_references = "REFERENCES" in text.upper()
        control_char_ratio = sum(
            1 for c in text if ord(c) < 0x20 and c != "\n"
        ) / max(len(text), 1)

        flag = ""
        if word_count < 500:
            flag = "TOO SHORT — likely failed extraction or scanned PDF"
        elif not has_references:
            flag = "NO REFERENCES SECTION FOUND — may be incomplete"
        elif control_char_ratio > 0.02:
            flag = "HIGH GARBLED-CHARACTER RATIO — heavy font-encoding corruption"

        results.append((fname, word_count, flag))
    return sorted(results, key=lambda x: x[1])


if __name__ == "__main__":
    RAW_DIR = "data/raw_papers"
    EXTRACTED_DIR = "data/extracted"

    failures = extract_all(RAW_DIR, EXTRACTED_DIR)
    if failures:
        print(f"{len(failures)} extraction failures:")
        for f in failures:
            print(f"  {f}")
    else:
        print("All files extracted without exceptions.")

    print("\nSanity check:")
    for fname, wc, flag in sanity_check(EXTRACTED_DIR):
        marker = f"  ⚠ {flag}" if flag else ""
        print(f"{fname}: {wc} words{marker}")
"""
Structured PDF extraction for Cited.

Extracts page-level document elements while preserving provenance for
retrieval and citations. Tables, captions, and figure crops are stored
separately from body text so they can receive element-aware treatment
during chunking.
"""

import json
import logging
import os
import re
from typing import Any

import pymupdf

logger = logging.getLogger(__name__)

CAPTION_RE = re.compile(
    r"^(Fig(?:ure)?\.?|Table)\s+(\d+)[.:]\s*(.+)",
    re.IGNORECASE,
)
EQUATION_NUMBER_RE = re.compile(r"\(\d{1,3}\)\s*$", re.MULTILINE)
MATH_TOKEN_RE = re.compile(
    r"[=<>]|[+\-*/^]|[∑∫√≈≤≥]|"
    r"\b(?:argmin|argmax|log|exp|softmax|loss)\b",
    re.IGNORECASE,
)

TABLE_EMPTY_CELL_THRESHOLD = 0.30


def boxes_overlap(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> bool:
    """Return True only when two rectangles have a real overlapping area."""
    ax0, ay0, ax1, ay1 = first
    bx0, by0, bx1, by1 = second

    return not (
        ax1 <= bx0
        or bx1 <= ax0
        or ay1 <= by0
        or by1 <= ay0
    )


def clean_text(text: str) -> str:
    """Remove unprintable control characters while preserving line breaks."""
    return "".join(
        character
        for character in text
        if character == "\n" or ord(character) >= 0x20
    )


def order_blocks(blocks: list[tuple[Any, ...]], page_width: float) -> list[tuple[Any, ...]]:
    """
    Return blocks in a reasonable reading order for single- and two-column pages.

    Full-width blocks above columns, such as titles and abstracts, are kept
    before the column text. Remaining full-width blocks are appended after it.
    """
    if not blocks:
        return []

    midpoint = page_width / 2
    wide_blocks = [
        block for block in blocks
        if (block[2] - block[0]) > 0.6 * page_width
    ]

    # A page dominated by wide blocks is treated as single-column.
    if len(wide_blocks) > len(blocks) * 0.5:
        return sorted(blocks, key=lambda block: block[1])

    narrow_blocks = [block for block in blocks if block not in wide_blocks]
    if not narrow_blocks:
        return sorted(wide_blocks, key=lambda block: block[1])

    first_column_y = min(block[1] for block in narrow_blocks)

    top_wide_blocks = [
        block for block in wide_blocks
        if block[3] <= first_column_y
    ]
    remaining_wide_blocks = [
        block for block in wide_blocks
        if block not in top_wide_blocks
    ]

    left_column = sorted(
        [block for block in narrow_blocks if block[0] < midpoint],
        key=lambda block: block[1],
    )
    right_column = sorted(
        [block for block in narrow_blocks if block[0] >= midpoint],
        key=lambda block: block[1],
    )

    return (
        sorted(top_wide_blocks, key=lambda block: block[1])
        + left_column
        + right_column
        + sorted(remaining_wide_blocks, key=lambda block: block[1])
    )


def escape_markdown_cell(value: Any) -> str:
    """Keep extracted table values valid inside a Markdown table cell."""
    text = str(value or "").replace("\n", "<br>")
    return text.replace("|", "\\|").strip()


def rows_to_markdown(rows: list[list[Any]]) -> str:
    """Convert extracted table rows into a rectangular Markdown table."""
    column_count = max(len(row) for row in rows)
    normalized_rows = [
        list(row) + [""] * (column_count - len(row))
        for row in rows
    ]

    header = normalized_rows[0]
    lines = [
        "| " + " | ".join(escape_markdown_cell(cell) for cell in header) + " |",
        "|" + "---|" * column_count,
    ]

    for row in normalized_rows[1:]:
        lines.append(
            "| " + " | ".join(escape_markdown_cell(cell) for cell in row) + " |"
        )

    return "\n".join(lines)

def expand_multiline_rows(rows: list[list[Any]]) -> tuple[list[list[Any]], bool]:
    """
    Repair a common PDF-table extraction failure.

    Some PDFs place several logical rows inside one cell, separated by
    newlines. Expand only when at least three non-empty cells have the
    same number of lines, which indicates that values still align by row.
    """
    repaired_rows: list[list[Any]] = []
    repair_applied = False

    for row in rows:
        cell_lines = [
            str(cell or "").splitlines() or [""]
            for cell in row
        ]

        non_empty_line_counts = [
            len(lines)
            for cell, lines in zip(row, cell_lines)
            if str(cell or "").strip()
        ]

        should_expand = (
            len(non_empty_line_counts) >= 3
            and len(set(non_empty_line_counts)) == 1
            and non_empty_line_counts[0] > 1
        )

        if not should_expand:
            repaired_rows.append(list(row))
            continue

        row_count = non_empty_line_counts[0]

        for row_index in range(row_count):
            repaired_rows.append(
                [
                    lines[row_index] if row_index < len(lines) else ""
                    for lines in cell_lines
                ]
            )

        repair_applied = True

    return repaired_rows, repair_applied

def extract_tables(
    page: pymupdf.Page,
    doc_id: str,
    page_number: int,
    crop_dir: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Extract tables as Markdown plus source crops.

    High empty-cell ratios are recorded as suspicious rather than rejected:
    academic tables can validly contain empty cells or merged headers.
    """
    tables: list[dict[str, Any]] = []
    warnings: list[str] = []

    try:
        finder = page.find_tables()
    except Exception as error:
        message = f"page {page_number}: table detection failed: {error}"
        logger.warning(message)
        return tables, [message]

    for extraction_index, table in enumerate(finder.tables, start=1):
        try:
            rows = table.extract()
        except Exception as error:
            message = (
                f"page {page_number}, candidate {extraction_index}: "
                f"table extraction failed: {error}"
            )
            logger.warning(message)
            warnings.append(message)
            continue

        if not rows or len(rows) < 2:
            warnings.append(
                f"page {page_number}, candidate {extraction_index}: "
                "ignored because fewer than two rows were extracted"
            )
            continue

        rows, row_repair_applied = expand_multiline_rows(rows)


        all_cells = [cell for row in rows for cell in row]

        empty_cell_ratio = sum(
            1 for cell in all_cells if not cell or not str(cell).strip()
        ) / max(len(all_cells), 1)

        max_lines_in_cell = max(
            str(cell or "").count("\n") + 1
            for cell in all_cells
        )

        is_suspicious = (
            empty_cell_ratio > TABLE_EMPTY_CELL_THRESHOLD
            or max_lines_in_cell > 3
            or row_repair_applied
        )

        if is_suspicious:
            warnings.append(
                f"page {page_number}, candidate {extraction_index}: "
                f"suspicious table extraction; "
                f"empty-cell ratio={empty_cell_ratio:.2f}, "
                f"max lines in cell={max_lines_in_cell}"
            )

        crop_path = os.path.join(
            crop_dir,
            f"{doc_id}_p{page_number}_table{extraction_index}.png",
        )
        page.get_pixmap(
            clip=pymupdf.Rect(table.bbox),
            dpi=150,
        ).save(crop_path)

        tables.append(
            {
                "element_type": "table",
                # This is the detector's index, not the paper's Table N label.
                "extraction_index": extraction_index,
                "bbox": list(table.bbox),
                "markdown": rows_to_markdown(rows),
                "source_image_path": crop_path,
                "empty_cell_ratio": round(empty_cell_ratio, 2),
                "max_lines_in_cell": max_lines_in_cell,
                "is_suspicious": is_suspicious,
                "row_repair_applied": row_repair_applied,
            }
        )

    return tables, warnings


def extract_figures(
    page: pymupdf.Page,
    doc_id: str,
    page_number: int,
    crop_dir: str,
) -> list[dict[str, Any]]:
    """
    Save crops of embedded raster images.

    Vector-drawn figures are not captured by this method. Captions remain
    separately retrievable even when a visual crop is unavailable.
    """
    figures: list[dict[str, Any]] = []

    for extraction_index, image in enumerate(page.get_images(full=True), start=1):
        xref = image[0]
        rectangles = page.get_image_rects(xref)

        if not rectangles:
            continue

        bbox = rectangles[0]
        if bbox.width < 40 or bbox.height < 40:
            continue

        crop_path = os.path.join(
            crop_dir,
            f"{doc_id}_p{page_number}_figure{extraction_index}.png",
        )
        page.get_pixmap(clip=bbox, dpi=150).save(crop_path)

        figures.append(
            {
                "element_type": "figure",
                "extraction_index": extraction_index,
                "bbox": list(bbox),
                "source_image_path": crop_path,
            }
        )

    return figures


def extract_captions_and_body(
    blocks: list[tuple[Any, ...]],
) -> tuple[list[dict[str, Any]], list[tuple[Any, ...]]]:
    """Separate simple figure/table captions from ordinary body-text blocks."""
    captions: list[dict[str, Any]] = []
    body_blocks: list[tuple[Any, ...]] = []

    for block in blocks:
        text = clean_text(block[4]).strip()
        match = CAPTION_RE.match(text)

        if not match:
            body_blocks.append(block)
            continue

        captions.append(
            {
                "element_type": "caption",
                "refers_to": (
                    "figure"
                    if match.group(1).lower().startswith("fig")
                    else "table"
                ),
                "number": int(match.group(2)),
                "text": text,
                "bbox": [block[0], block[1], block[2], block[3]],
            }
        )

    return captions, body_blocks


def has_equation_hint(body_text: str) -> bool:
    """
    Return a conservative equation hint.

    This is not equation extraction. It only determines whether retaining a
    full-page crop may help a user inspect an equation in the original layout.
    """
    return bool(
        EQUATION_NUMBER_RE.search(body_text)
        and MATH_TOKEN_RE.search(body_text)
    )


def is_likely_scanned(
    page: pymupdf.Page,
    body_blocks: list[tuple[Any, ...]],
) -> bool:
    """Flag, but do not reject, pages that may require later OCR review."""
    text_character_count = sum(
        len(clean_text(block[4])) for block in body_blocks
    )

    has_large_image = any(
        rectangle.width * rectangle.height
        > 0.5 * page.rect.width * page.rect.height
        for image in page.get_images(full=True)
        for rectangle in page.get_image_rects(image[0])
    )

    return text_character_count < 200 and has_large_image


def extract_document(
    pdf_path: str,
    doc_id: str,
    crop_dir: str,
) -> dict[str, Any]:
    """Extract one PDF into page-level, typed document elements."""
    os.makedirs(crop_dir, exist_ok=True)
    pages: list[dict[str, Any]] = []

    with pymupdf.open(pdf_path) as document:
        for page in document:
            page_number = page.number + 1
            raw_blocks = page.get_text("blocks")

            tables, extraction_warnings = extract_tables(
                page=page,
                doc_id=doc_id,
                page_number=page_number,
                crop_dir=crop_dir,
            )
            table_bboxes = [table["bbox"] for table in tables]

            non_table_blocks = [
                block
                for block in raw_blocks
                if not any(
                    boxes_overlap(
                        (block[0], block[1], block[2], block[3]),
                        table_bbox,
                    )
                    for table_bbox in table_bboxes
                )
            ]

            captions, body_blocks = extract_captions_and_body(non_table_blocks)
            # Embedded image objects are often figure fragments, not logical figures.
            # Keep captions and preserve the complete source page instead.
            figures = []
            has_figure_caption = any(
                caption["refers_to"] == "figure"
                for caption in captions
            )

            ordered_body_blocks = order_blocks(body_blocks, page.rect.width)
            body_text = "\n".join(
                clean_text(block[4]) for block in ordered_body_blocks
            ).strip()

            equation_hint = has_equation_hint(body_text)
            scanned_hint = is_likely_scanned(page, body_blocks)

            page_crop_path = None
            if equation_hint or scanned_hint or has_figure_caption:
                page_crop_path = os.path.join(
                    crop_dir,
                    f"{doc_id}_p{page_number}_full.png",
                )
                page.get_pixmap(dpi=150).save(page_crop_path)

            pages.append(
                {
                    "page_number": page_number,
                    "body_text": body_text,
                    "tables": tables,
                    "captions": captions,
                    "figures": figures,
                    "has_equation_hint": equation_hint,
                    "is_likely_scanned": scanned_hint,
                    "page_crop_path": page_crop_path,
                    "extraction_warnings": extraction_warnings,
                }
            )

    return {
        "doc_id": doc_id,
        "source_pdf": pdf_path,
        "pages": pages,
    }


def extract_all(
    raw_dir: str,
    structured_dir: str,
    crop_dir: str,
) -> list[str]:
    """Extract each PDF independently so one bad file does not stop the batch."""
    os.makedirs(structured_dir, exist_ok=True)
    failures: list[str] = []

    for pdf_filename in sorted(os.listdir(raw_dir)):
        if not pdf_filename.lower().endswith(".pdf"):
            continue

        doc_id = pdf_filename[:-4]
        pdf_path = os.path.join(raw_dir, pdf_filename)

        try:
            result = extract_document(pdf_path, doc_id, crop_dir)
            output_path = os.path.join(structured_dir, f"{doc_id}.json")

            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(result, output_file, indent=2)
        except Exception as error:
            message = f"{pdf_filename}: {error}"
            logger.exception("Extraction failed for %s", pdf_filename)
            failures.append(message)

    return failures


def sanity_check(structured_dir: str) -> None:
    """Print a corpus-level extraction report for manual review."""
    rows = []

    for filename in sorted(os.listdir(structured_dir)):
        if not filename.endswith(".json"):
            continue

        with open(
            os.path.join(structured_dir, filename),
            "r",
            encoding="utf-8",
        ) as input_file:
            document = json.load(input_file)

        word_count = sum(
            len(page["body_text"].split())
            for page in document["pages"]
        )
        table_count = sum(
            len(page["tables"])
            for page in document["pages"]
        )
        suspicious_tables = [
            (
                page["page_number"],
                table["extraction_index"],
                table["empty_cell_ratio"],
            )
            for page in document["pages"]
            for table in page["tables"]
            if table["is_suspicious"]
        ]
        scanned_pages = [
            page["page_number"]
            for page in document["pages"]
            if page["is_likely_scanned"]
        ]
        warning_count = sum(
            len(page["extraction_warnings"])
            for page in document["pages"]
        )

        flags = []
        if word_count < 500:
            flags.append("LOW WORD COUNT")
        if scanned_pages:
            flags.append(f"POSSIBLE SCANNED PAGES: {scanned_pages}")
        if suspicious_tables:
            flags.append(f"SUSPICIOUS TABLES: {suspicious_tables}")
        if warning_count:
            flags.append(f"EXTRACTION WARNINGS: {warning_count}")

        rows.append(
            (
                document["doc_id"],
                word_count,
                table_count,
                suspicious_tables,
                flags,
            )
        )

    print(f"{'doc_id':<55} {'words':>7} {'tables':>7}")
    for doc_id, word_count, table_count, _, flags in sorted(
        rows,
        key=lambda row: row[1],
    ):
        print(f"{doc_id[:55]:<55} {word_count:>7} {table_count:>7}")
        for flag in flags:
            print(f"  WARNING: {flag}")

    flagged_count = sum(1 for row in rows if row[4])
    print(f"\n{len(rows)} documents processed, {flagged_count} flagged for review.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    failures = extract_all(
        raw_dir="data/raw_papers",
        structured_dir="data/extracted_structured",
        crop_dir="data/crops",
    )

    if failures:
        print(f"{len(failures)} extraction failures:")
        for failure in failures:
            print(f"  {failure}")
    else:
        print("All files extracted without exceptions.")

    print()
    sanity_check("data/extracted_structured")



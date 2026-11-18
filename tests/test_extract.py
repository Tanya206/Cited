from app.ingestion.extract import CAPTION_RE, parse_caption_number


def test_roman_and_arabic_numbers():
    assert parse_caption_number("3") == 3
    assert parse_caption_number("IV") == 4
    assert parse_caption_number("XIV") == 14


def test_ieee_table_caption_matches():
    assert CAPTION_RE.match("TABLE III: Ablation studies on Lcon.")
    assert CAPTION_RE.match("Fig. 2: Effect of continuity loss.")

# --- Overlap rule and decision D4: never silently remove text -------------------

from app.ingestion.extract import (  # noqa: E402
    TABLE_BLOCK_INSIDE_RATIO,
    is_header_numeric,
    overlap_fraction,
    remove_table_blocks,
)

TABLE_BOX = (0.0, 0.0, 100.0, 100.0)


def _block(x0, y0, x1, y1, text="block"):
    # PyMuPDF block tuple: (x0, y0, x1, y1, text, block_no, block_type)
    return (x0, y0, x1, y1, text, 0, 0)


def _table(is_suspicious):
    return {"bbox": list(TABLE_BOX), "is_suspicious": is_suspicious}


def test_overlap_fraction_is_share_of_the_block_inside_the_table():
    assert overlap_fraction((10, 10, 20, 20), TABLE_BOX) == 1.0
    assert overlap_fraction((200, 200, 210, 210), TABLE_BOX) == 0.0
    assert overlap_fraction((90, 0, 110, 10), TABLE_BOX) == 0.5


def test_usable_table_removes_only_blocks_mostly_inside_it():
    inside = _block(10, 10, 50, 50, "row inside the table")
    mostly_inside = _block(0, 0, 100, 85, "85 percent inside")
    caption_touching = _block(0, 95, 100, 120, "Table 2: caption below the table")
    kept = remove_table_blocks([inside, mostly_inside, caption_touching], [_table(False)])
    assert kept == [caption_touching]
    assert TABLE_BLOCK_INSIDE_RATIO == 0.8


def test_suspicious_table_never_removes_body_text():
    inside = _block(10, 10, 50, 50, "values of a table that failed the checks")
    assert remove_table_blocks([inside], [_table(True)]) == [inside]


def test_numeric_header_is_flagged_and_word_header_is_not():
    assert is_header_numeric(["1", "2", "0.85", None])
    assert is_header_numeric(["", "10", "20"])
    assert not is_header_numeric(["Method", "mIoU", "Acc"])
    assert not is_header_numeric([None, "k", "NMI"])

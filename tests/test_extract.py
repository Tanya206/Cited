from app.ingestion.extract import CAPTION_RE, parse_caption_number


def test_roman_and_arabic_numbers():
    assert parse_caption_number("3") == 3
    assert parse_caption_number("IV") == 4
    assert parse_caption_number("XIV") == 14


def test_ieee_table_caption_matches():
    assert CAPTION_RE.match("TABLE III: Ablation studies on Lcon.")
    assert CAPTION_RE.match("Fig. 2: Effect of continuity loss.")
from app.core.text_utils import match_key, normalize


def test_normalize_folds_pdf_ligatures_and_whitespace() -> None:
    assert normalize("  classiﬁers\n  use   dense\toutputs ") == "classifiers use dense outputs"


def test_match_key_tolerates_line_break_hyphenation() -> None:
    # G09: the PDF hyphenates "correlated" across a line break, but the
    # reviewer copies the quote as it reads on the page. Evidence matching is
    # a containment test of the quote inside the indexed chunk, so assert that.
    quote = match_key("resulting in two correlated views")
    chunk = match_key("resulting in two cor- related views of the same example")
    assert quote in chunk


def test_match_key_is_case_and_punctuation_insensitive() -> None:
    assert match_key("SimCLR's projection head g(·)") == match_key("simclr s projection head g")


def test_match_key_keeps_digits_distinct() -> None:
    # Alphanumeric folding must not let near-identical numbers match.
    assert match_key("mIoU is 0.999") != match_key("mIoU is 0.99")
    assert match_key("m 0.999") != match_key("m 0.9")

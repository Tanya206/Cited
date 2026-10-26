"""Shared text normalization for PDF-derived evidence matching."""

import unicodedata


def normalize(text: str) -> str:
    """Fold PDF ligatures and whitespace before comparing human-copied quotes."""
    return " ".join(unicodedata.normalize("NFKC", text).split())


def match_key(text: str) -> str:
    """Collapse text to letters and digits so wrapped-line hyphenation still matches.

    PDF extraction keeps the hyphen it inserted at a line break
    (``cor- related views``) while a person copying the quote writes
    ``correlated views``. Reducing both sides to alphanumeric characters
    makes those forms compare equal, and digits are preserved so that
    ``0.99`` and ``0.999`` can never be confused for one another.
    """
    folded = unicodedata.normalize("NFKC", text).casefold()
    return "".join(character for character in folded if character.isalnum())

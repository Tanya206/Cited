import pytest

from app.core.generation import GenerationError, NO_ANSWER, _parse_json


def test_parse_json_accepts_a_fenced_response() -> None:
    payload = _parse_json('```json\n{"answer": "Supported", "citation_chunk_ids": ["c1"]}\n```')

    assert payload["citation_chunk_ids"] == ["c1"]


def test_parse_json_rejects_non_json_response() -> None:
    with pytest.raises(GenerationError, match="valid JSON"):
        _parse_json("I think the answer is yes")


def test_refusal_text_is_stable() -> None:
    assert "enough evidence" in NO_ANSWER

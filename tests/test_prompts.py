"""The answer prompt is versioned configuration: it loads, it is validated, and v1 is frozen."""

from pathlib import Path

import pytest

import app.core.generation as generation
from app.core.prompts import PromptConfigError, load_prompt
from tests.prompt_fixture import capture_prompts

FIXTURES = Path(__file__).parent / "fixtures"

# Changing prompts/answer_v1.yaml in any way changes this hash. That is intended: a changed
# prompt must become answer_v2.yaml so saved results keep naming the prompt they used.
ANSWER_V1_SHA256 = "fc7bdc4fe0b1727d2071c647c5047c4cb0f3e18bf275a311f417ba5e4cb0d911"


def test_v1_loads_with_version_and_unchanged_refusal():
    prompt = load_prompt("answer_v1")
    assert prompt.version == "answer_v1"
    assert prompt.refusal == "I don't have enough evidence in the indexed papers to answer that reliably."
    assert generation.NO_ANSWER == prompt.refusal


def test_v1_file_is_frozen():
    assert load_prompt("answer_v1").sha256 == ANSWER_V1_SHA256


def test_v1_renders_the_same_text_the_inline_fstrings_produced(monkeypatch):
    """Snapshots were captured from generation.py at commit 2c61b69, before the move."""
    sent, result = capture_prompts(generation, monkeypatch)
    assert sent[0] == (FIXTURES / "answer_v1_answer.txt").read_text(encoding="utf-8")
    assert sent[1] == (FIXTURES / "answer_v1_repair.txt").read_text(encoding="utf-8")
    assert result == ("Uses crops.", ["simclr_c0001"], False)


def test_unknown_version_is_rejected():
    with pytest.raises(PromptConfigError, match="no prompt file"):
        load_prompt("answer_v999")


def test_path_tricks_are_rejected():
    with pytest.raises(PromptConfigError):
        load_prompt("../requirements")


def test_missing_placeholder_is_rejected(tmp_path, monkeypatch):
    import app.core.prompts as prompts

    (tmp_path / "broken_v1.yaml").write_text(
        "version: broken_v1\n"
        "refusal: No.\n"
        "evidence: {item: '${chunk_id} ${doc_id} ${page_number} ${text}', separator: '', max_characters: 10}\n"
        "answer: 'Question only: ${question}'\n"
        "repair: '${prompt} ${allowed_ids} ${refusal}'\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(prompts, "PROMPTS_DIR", tmp_path)
    load_prompt.cache_clear()
    try:
        with pytest.raises(PromptConfigError, match="lacks placeholders"):
            load_prompt("broken_v1")
    finally:
        load_prompt.cache_clear()

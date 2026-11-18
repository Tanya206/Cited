"""Load the versioned answer prompt from prompts/<version>.yaml.

The prompt is configuration, not code: changing it creates a new file and a new version,
and that version (plus a hash of the file) is recorded in every trace and eval result.
"""

import hashlib
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from string import Template

import yaml

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
DEFAULT_PROMPT_VERSION = "answer_v1"

_REQUIRED_PLACEHOLDERS = {
    "answer": {"refusal", "question", "evidence"},
    "repair": {"prompt", "allowed_ids", "refusal"},
    "evidence.item": {"chunk_id", "doc_id", "page_number", "text"},
}


class PromptConfigError(ValueError):
    """The prompt file is missing, malformed, or lacks a required placeholder."""


@dataclass(frozen=True)
class AnswerPrompt:
    version: str
    sha256: str
    refusal: str
    answer: Template
    repair: Template
    evidence_item: Template
    evidence_separator: str
    evidence_max_characters: int

    def render_evidence(self, chunks: list[dict]) -> str:
        """Join chunks with their IDs; stop before exceeding the character budget."""
        parts: list[str] = []
        used = 0
        for chunk in chunks:
            part = self.evidence_item.substitute(
                chunk_id=chunk["chunk_id"],
                doc_id=chunk["doc_id"],
                page_number=chunk["page_number"],
                text=chunk["text"],
            )
            if used + len(part) > self.evidence_max_characters:
                break
            parts.append(part)
            used += len(part)
        return self.evidence_separator.join(parts)

    def render_answer(self, question: str, chunks: list[dict]) -> str:
        return self.answer.substitute(
            refusal=self.refusal, question=question, evidence=self.render_evidence(chunks)
        )

    def render_repair(self, prompt: str, allowed_ids: str) -> str:
        return self.repair.substitute(prompt=prompt, allowed_ids=allowed_ids, refusal=self.refusal)


def _file_sha256(path: Path) -> str:
    # Normalise line endings so Windows (CRLF checkout) and Linux CI agree on the hash.
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _template(data: dict, key: str) -> Template:
    value = data
    for part in key.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    if not isinstance(value, str) or not value:
        raise PromptConfigError(f"prompt field {key!r} must be a non-empty string")
    template = Template(value)
    missing = _REQUIRED_PLACEHOLDERS[key] - set(template.get_identifiers())
    if missing:
        raise PromptConfigError(f"prompt field {key!r} lacks placeholders: {sorted(missing)}")
    return template


@lru_cache(maxsize=None)
def load_prompt(version: str | None = None) -> AnswerPrompt:
    """Load a prompt by version; default from PROMPT_VERSION, else answer_v1."""
    name = version or os.getenv("PROMPT_VERSION") or DEFAULT_PROMPT_VERSION
    path = PROMPTS_DIR / f"{name}.yaml"
    if path.parent != PROMPTS_DIR or not path.is_file():
        raise PromptConfigError(f"no prompt file for version {name!r} in {PROMPTS_DIR}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PromptConfigError(f"{path.name} must contain a mapping")
    if data.get("version") != name:
        raise PromptConfigError(f"{path.name}: version field must equal the file name {name!r}")
    refusal = data.get("refusal")
    if not isinstance(refusal, str) or not refusal.strip():
        raise PromptConfigError(f"{path.name}: refusal must be a non-empty string")
    evidence = data.get("evidence") or {}
    max_characters = evidence.get("max_characters")
    if not isinstance(max_characters, int) or max_characters <= 0:
        raise PromptConfigError(f"{path.name}: evidence.max_characters must be a positive integer")
    return AnswerPrompt(
        version=name,
        sha256=_file_sha256(path),
        refusal=refusal,
        answer=_template(data, "answer"),
        repair=_template(data, "repair"),
        evidence_item=_template(data, "evidence.item"),
        evidence_separator=str(evidence.get("separator", "")),
        evidence_max_characters=max_characters,
    )

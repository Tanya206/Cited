"""Grounded answer generation with citation IDs validated in code."""

import json
import os
import re

from groq import Groq


# Groq retired the previous Llama default for developer-tier accounts.
# Keep this configurable via GROQ_MODEL for future provider changes.
DEFAULT_MODEL = "openai/gpt-oss-20b"
NO_ANSWER = "I don't have enough evidence in the indexed papers to answer that reliably."


class GenerationError(RuntimeError):
    """Raised when the model response cannot be verified as a cited answer."""


def _context(chunks: list[dict], max_characters: int = 24_000) -> str:
    parts: list[str] = []
    used = 0
    for chunk in chunks:
        part = (
            f"[chunk_id={chunk['chunk_id']}; paper={chunk['doc_id']}; "
            f"page={chunk['page_number']}]\n{chunk['text']}"
        )
        if used + len(part) > max_characters:
            break
        parts.append(part)
        used += len(part)
    return "\n\n---\n\n".join(parts)


def _parse_json(content: str) -> dict:
    """Accept JSON returned inside an occasional Markdown code fence."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise GenerationError("The model did not return valid JSON.") from error
    if not isinstance(payload, dict):
        raise GenerationError("The model response must be a JSON object.")
    return payload


def generate_cited_answer(query: str, chunks: list[dict]) -> tuple[str, list[str], bool]:
    """Return an answer and only citation IDs that exist in ``chunks``."""
    if not chunks:
        return NO_ANSWER, [], True

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise GenerationError("GROQ_API_KEY is not configured.")

    prompt = f"""You answer questions only from the supplied research-paper evidence.
If the evidence does not support an answer, return the exact refusal text:
{NO_ANSWER}

Return JSON only, with this shape:
{{"answer": "...", "citation_chunk_ids": ["chunk-id"]}}

Rules:
- Do not use knowledge outside the evidence.
- Every factual sentence in the answer must be supported by one or more IDs in citation_chunk_ids.
- Use only chunk IDs that appear in the evidence.
- Do not invent numerical results, titles, or page numbers.

Question: {query}

Evidence:
{_context(chunks)}"""

    client = Groq(api_key=api_key)
    request = {
        "model": os.getenv("GROQ_MODEL", DEFAULT_MODEL),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    try:
        response = client.chat.completions.create(
            **request,
            response_format={"type": "json_object"},
        )
    except Exception as error:
        # Some provider/model responses fail structured-output validation before
        # returning content. Retry with local JSON parsing as a fallback.
        try:
            response = client.chat.completions.create(**request)
        except Exception as retry_error:
            raise GenerationError(
                f"The answer provider failed after a JSON retry: {retry_error}"
            ) from retry_error

    payload = _parse_json(response.choices[0].message.content or "")
    answer = str(payload.get("answer", "")).strip()
    citation_ids = payload.get("citation_chunk_ids", [])
    valid_ids = {chunk["chunk_id"] for chunk in chunks}

    if not answer:
        raise GenerationError("The model returned an empty answer.")
    if answer == NO_ANSWER:
        return answer, [], True
    if not isinstance(citation_ids, list) or not citation_ids:
        raise GenerationError("The model returned an uncited answer.")

    citations = [str(chunk_id) for chunk_id in citation_ids]
    if any(chunk_id not in valid_ids for chunk_id in citations):
        raise GenerationError("The model cited evidence that was not retrieved.")
    return answer, list(dict.fromkeys(citations)), False

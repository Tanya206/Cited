"""Grounded answer generation with citation IDs validated in code."""

import json
import re

from openai import APIConnectionError, APIStatusError, BadRequestError, OpenAI, RateLimitError

from app.core.llm_client import create_llm_client


# The model is configured in app/core/llm_client.py (LLM_MODEL, legacy GROQ_MODEL).
NO_ANSWER = "I don't have enough evidence in the indexed papers to answer that reliably."


class GenerationError(RuntimeError):
    """Raised when the model response cannot be verified as a cited answer."""


class ProviderRateLimitError(GenerationError):
    """The provider refused the request with HTTP 429 (rate or daily quota limit)."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


def _retry_after_seconds(error: APIStatusError) -> int | None:
    """Read the provider's Retry-After header, if it sent one in seconds."""
    value = error.response.headers.get("retry-after") if error.response is not None else None
    try:
        return max(1, int(float(value))) if value else None
    except ValueError:
        return None


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


def _provider_error(error: Exception) -> GenerationError:
    """Map an SDK error to ours, keeping the provider's message for the logs."""
    if isinstance(error, RateLimitError):
        return ProviderRateLimitError(
            f"The answer provider is rate limited: {error}", _retry_after_seconds(error)
        )
    return GenerationError(f"The answer provider failed: {error}")


def _request_payload(client: OpenAI, request: dict) -> dict:
    """Call an OpenAI-compatible provider in JSON mode, falling back to plain text.

    Only HTTP 400 means JSON mode itself was rejected (for example Groq's
    json_validate_failed), so only 400 earns the one retry without it. A 429
    or a server error is not fixed by dropping JSON mode; retrying would add a
    wasted call and hide the real cause, so it is raised at once.
    """
    try:
        try:
            response = client.chat.completions.create(
                **request,
                response_format={"type": "json_object"},
            )
        except BadRequestError:
            response = client.chat.completions.create(**request)
    except (APIStatusError, APIConnectionError) as error:
        raise _provider_error(error) from error
    return _parse_json(response.choices[0].message.content or "")


def generate_cited_answer(query: str, chunks: list[dict]) -> tuple[str, list[str], bool]:
    """Return an answer and only citation IDs that exist in ``chunks``."""
    if not chunks:
        return NO_ANSWER, [], True

    client, settings = create_llm_client()
    api_key = settings.api_key
    if not api_key:
        raise GenerationError("LLM_API_KEY is not configured.")

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

    request = {
        "model": settings.model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": settings.max_tokens,
    }
    payload = _request_payload(client, request)
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
        allowed_ids = ", ".join(sorted(valid_ids))
        repair_request = {
            **request,
            "messages": [{
                "role": "user",
                "content": (
                    f"{prompt}\n\n"
                    "Your previous response cited an unavailable chunk. "
                    "Return JSON again and use only these allowed citation IDs: "
                    f"{allowed_ids}. If the evidence is insufficient, return the "
                    f"exact refusal text: {NO_ANSWER}"
                ),
            }],
        }
        repaired = _request_payload(client, repair_request)
        repaired_answer = str(repaired.get("answer", "")).strip()
        repaired_ids = repaired.get("citation_chunk_ids", [])
        if repaired_answer == NO_ANSWER:
            return NO_ANSWER, [], True
        if isinstance(repaired_ids, list):
            repaired_citations = [str(chunk_id) for chunk_id in repaired_ids]
            if repaired_answer and repaired_citations and all(
                chunk_id in valid_ids for chunk_id in repaired_citations
            ):
                return repaired_answer, list(dict.fromkeys(repaired_citations)), False
        # A refusal is safer than returning an answer with unverifiable sources.
        return NO_ANSWER, [], True
    return answer, list(dict.fromkeys(citations)), False

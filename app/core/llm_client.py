"""Provider-neutral configuration for OpenAI-compatible chat APIs."""

import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class LLMSettings:
    api_key: str
    base_url: str
    model: str
    max_tokens: int


def get_llm_settings() -> LLMSettings:
    """Read one common configuration, retaining old Groq names as fallbacks."""
    api_key = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL") or "https://api.groq.com/openai/v1"
    model = os.getenv("LLM_MODEL") or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    return LLMSettings(api_key=api_key, base_url=base_url, model=model, max_tokens=max_tokens)


def create_llm_client() -> tuple[OpenAI, LLMSettings]:
    settings = get_llm_settings()
    return OpenAI(api_key=settings.api_key, base_url=settings.base_url), settings

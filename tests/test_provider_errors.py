"""Provider failures: which ones are retried, and what HTTP status the API returns."""

from types import SimpleNamespace

import httpx
import openai
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import routes
from app.core.generation import GenerationError, ProviderRateLimitError, _request_payload

REQUEST = {"model": "m", "messages": [{"role": "user", "content": "q"}]}


def _status_error(cls, status, headers=None):
    response = httpx.Response(
        status, headers=headers or {}, request=httpx.Request("POST", "https://provider.test/v1")
    )
    return cls(f"HTTP {status} from provider", response=response, body=None)


class FakeClient:
    """Stands in for openai.OpenAI; replays scripted results and records the calls."""

    def __init__(self, *results):
        self.results = list(results)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **request):
        self.calls.append(request)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])


def test_rate_limit_is_not_retried_and_keeps_retry_after():
    client = FakeClient(_status_error(openai.RateLimitError, 429, {"retry-after": "7"}))
    with pytest.raises(ProviderRateLimitError) as caught:
        _request_payload(client, REQUEST)
    assert caught.value.retry_after == 7
    assert len(client.calls) == 1


def test_json_mode_rejection_retries_once_without_json_mode():
    client = FakeClient(
        _status_error(openai.BadRequestError, 400),
        '{"answer": "ok", "citation_chunk_ids": ["c1"]}',
    )
    assert _request_payload(client, REQUEST)["answer"] == "ok"
    assert "response_format" in client.calls[0]
    assert "response_format" not in client.calls[1]


def test_server_error_is_not_retried():
    client = FakeClient(_status_error(openai.InternalServerError, 500))
    with pytest.raises(GenerationError, match="provider failed") as caught:
        _request_payload(client, REQUEST)
    assert not isinstance(caught.value, ProviderRateLimitError)
    assert len(client.calls) == 1


def _api(monkeypatch, error):
    monkeypatch.setattr(routes, "hybrid_retrieve", lambda *args, **kwargs: [])

    def fail(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(routes, "generate_cited_answer", fail)
    app = FastAPI()
    app.include_router(routes.router)
    reranker = SimpleNamespace(rerank=lambda query, candidates, top_k: [])
    app.state.services = SimpleNamespace(
        collection=None, embed_model=None, bm25_retriever=None, chunk_id_map=[], reranker=reranker
    )
    return TestClient(app)


def test_api_returns_503_with_retry_after_on_rate_limit(monkeypatch):
    client = _api(monkeypatch, ProviderRateLimitError("rate_limit_exceeded: try again in 7s", 7))
    response = client.post("/answer", json={"query": "What does SimCLR use?"})
    assert response.status_code == 503
    assert response.headers["retry-after"] == "7"
    # eval/collect_answer_runs.py reads the provider message from the body.
    assert "rate_limit_exceeded" in response.json()["detail"]


def test_api_returns_502_on_other_provider_failure(monkeypatch):
    client = _api(monkeypatch, GenerationError("The answer provider failed: HTTP 500"))
    response = client.post("/answer", json={"query": "What does SimCLR use?"})
    assert response.status_code == 502

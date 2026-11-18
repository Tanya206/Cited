"""The prompt version travels from the API response into answer runs and Ragas results."""

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import routes
from app.core.prompts import load_prompt
from eval.run_ragas import attach_run_metadata, sample_fields


def test_api_response_names_the_prompt(monkeypatch):
    monkeypatch.setattr(routes, "hybrid_retrieve", lambda *args, **kwargs: [])
    app = FastAPI()
    app.include_router(routes.router)
    app.state.services = SimpleNamespace(
        collection=None, embed_model=None, bm25_retriever=None, chunk_id_map=[],
        reranker=SimpleNamespace(rerank=lambda query, candidates, top_k: []),
    )
    # No chunks retrieved: the refusal path, no provider call needed.
    body = TestClient(app).post("/answer", json={"query": "What does SimCLR use?"}).json()
    assert body["refused"] is True
    assert body["prompt_version"] == "answer_v1"
    assert body["prompt_sha256"] == load_prompt("answer_v1").sha256
    assert body["generator_model"]  # from LLM_MODEL or the default


def test_validation_refusal_sends_no_prompt_and_says_so(monkeypatch):
    app = FastAPI()
    app.include_router(routes.router)
    body = TestClient(app).post("/answer", json={"query": "simclr"}).json()
    assert body["refused"] is True
    assert body["prompt_version"] is None


ROW = {
    "id": "G01", "user_input": "q", "response": "a", "retrieved_contexts": ["c"],
    "reference": "r", "reference_contexts": ["rc"], "refused": False,
    "prompt_version": "answer_v1", "prompt_sha256": "abc",
}


def test_ragas_samples_get_only_scored_fields():
    assert sample_fields(ROW) == {
        "user_input": "q", "response": "a", "retrieved_contexts": ["c"],
        "reference": "r", "reference_contexts": ["rc"],
    }


def test_ragas_results_carry_id_and_prompt_version():
    out = attach_run_metadata([{"user_input": "q", "faithfulness": 1.0}], [ROW])
    assert out == [{
        "id": "G01", "prompt_version": "answer_v1", "prompt_sha256": "abc",
        "user_input": "q", "faithfulness": 1.0,
    }]


def test_old_runs_without_a_version_stay_unknown():
    old = {key: value for key, value in ROW.items() if not key.startswith("prompt")}
    assert attach_run_metadata([{"faithfulness": 0.5}], [old])[0]["prompt_version"] is None


def test_result_count_mismatch_is_an_error():
    with pytest.raises(ValueError):
        attach_run_metadata([], [ROW])

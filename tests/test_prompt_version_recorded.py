"""The prompt version travels from the API response into answer runs and Ragas results."""

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import routes
from app.core.prompts import load_prompt
from eval.run_ragas import sample_fields


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


# --- Judge configuration and resume (eval/run_ragas.py) -----------------------------------

from types import SimpleNamespace as _NS  # noqa: E402

from eval.run_ragas import completed_pairs, resolve_judge, select_metrics  # noqa: E402

GENERATOR = _NS(api_key="gen-key", base_url="https://generator.test/v1", model="gen-model")


def test_partial_judge_config_is_refused_so_keys_never_cross_providers():
    with pytest.raises(SystemExit, match="RAGAS_BASE_URL"):
        resolve_judge({"RAGAS_API_KEY": "judge-key"}, GENERATOR)


def test_full_judge_config_is_used_and_separate_from_the_generator():
    env = {"RAGAS_API_KEY": "judge-key", "RAGAS_BASE_URL": "https://judge.test/v1", "RAGAS_MODEL": "judge-model"}
    judge = resolve_judge(env, GENERATOR)
    assert judge == {"api_key": "judge-key", "base_url": "https://judge.test/v1",
                     "model": "judge-model", "shares_generator_quota": False}


def test_no_judge_config_falls_back_and_says_it_shares_quota():
    judge = resolve_judge({}, GENERATOR)
    assert judge["model"] == "gen-model" and judge["shares_generator_quota"] is True


def test_resume_skips_scored_item_metric_pairs(tmp_path):
    path = tmp_path / "runs.jsonl"
    path.write_text('{"id": "G09", "metric": "faithfulness", "score": 1.0}\n', encoding="utf-8")
    assert completed_pairs(path) == {("G09", "faithfulness")}
    assert completed_pairs(tmp_path / "missing.jsonl") == set()


def test_metrics_run_in_the_documented_order():
    assert select_metrics("context_recall,faithfulness") == ["faithfulness", "context_recall"]
    with pytest.raises(SystemExit):
        select_metrics("bleu")

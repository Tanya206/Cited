# Evaluation and Design Decisions

## What is complete

The golden dataset in `eval/golden_dataset.json` is the contract for the
project. Each answerable item has an expected document and page; each verified
item also has a verbatim evidence quote. Refusal and clarification cases do
not require evidence. Run `python -m eval.validate_golden` for a progress
report and `python -m eval.validate_golden --strict` before treating the set
as a release gate.

The evidence review is intentionally separate from retrieval scoring. A quote
can be structurally valid but still be a poor explanation of the answer, so a
human must approve proposed quotes in `eval/EVIDENCE_REVIEW.md`.

## Retrieval baseline

From the repository root, with the local corpus indexed:

```powershell
python -m eval.run_retrieval_eval --out eval/baseline_retrieval.json
python -m eval.run_retrieval_eval --rerank --out eval/baseline_retrieval_reranked.json
```

The report includes document hit rate, page hit rate, document MRR, page MRR,
and category breakdowns. A document hit answers “did we find the right paper?”;
a page hit is stricter and answers “did we find the evidence location?”

## Ragas run

Start the API in one terminal, then run these from a second terminal:

```powershell
python -m eval.collect_answer_runs
python -m eval.run_ragas
```

Ragas measures faithfulness, response/answer relevancy, context precision,
and context recall. It is not in the PR blocking path because it calls an
evaluator LLM, needs credentials, and is not deterministic enough for every
commit. The saved `eval/answer_runs.jsonl` and `eval/ragas_results.json` are
local evaluation artifacts and must not be committed.

## Langfuse tracing

Set `LANGFUSE_ENABLED=true`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and
optionally `LANGFUSE_HOST` in `.env`, then restart Uvicorn. One trace covers
validation, hybrid retrieval, reranking, and answer generation. Only query
metadata, counts, chunk IDs, citations, and the final answer are recorded;
full corpus chunks are not sent as trace metadata by this integration.

Langfuse is optional and tracing errors are isolated from the answer path.
LangGraph is deliberately not used: this request is a linear pipeline, not a
stateful multi-step workflow. It becomes justified only when the product adds
branching retries, tool loops, or persistent user/session state.

## CI decision

GitHub Actions runs `pytest` and the structural golden-dataset validator on
every push and pull request. The tests use small deterministic fixtures and do
not require the private/copyrighted corpus, Hugging Face downloads, Groq, or
Langfuse credentials. Full-corpus retrieval and Ragas are explicit local or
scheduled jobs because putting the corpus and API secrets into every PR would
make the gate expensive, brittle, and difficult to reproduce.

## Why this architecture

- BM25 plus BGE vectors plus reciprocal-rank fusion gives lexical and semantic
  recall while keeping the ranking logic inspectable.
- A cross-encoder reranker is applied after broad retrieval, which improves
  precision without embedding the entire corpus again.
- FastAPI owns the cited-answer contract; Streamlit is only a presentation
  client.
- Ragas evaluates answer quality; deterministic retrieval metrics evaluate
  search quality. Neither replaces the other.
- Langfuse provides request-level observability, while the golden dataset is
  the durable regression contract. GitHub Actions blocks only on checks that
  are free and deterministic.

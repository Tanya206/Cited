# Definition of Done

Ratified by the owner at gate G1 on 2026-11-18. Proposed in the workstream 0 audit
(`docs/CHANGES.md`, 2026-11-14 entry). Thresholds are set only after baselines exist.

**Hard end date for the build:** Thursday 2026-11-19. At that date, unfinished items become
documented limitations in `docs/GAPS.md` and the README, and workstream 5H starts.

## Reproducibility rule (applies to every number below)

Every number comes from a committed command. Its result file records: commit SHA, config,
generator model, judge model, embedding model, prompt version, golden set version (v1 or v2),
n, k and date. A v1 number is never compared with a v2 number. No accuracy claims: numbers are
"measured against a golden set written by the author" (D5).

## Results

- [ ] **Retrieval comparison ladder** on golden v1 and v2 separately, all at the same k
      (k=6 and k=20): vector only, BM25 only, hybrid RRF, + query expansion, + rerank.
      Doc hit, page hit, doc MRR, page MRR. Runs first in 5B, before any LLM spend. No LLM.
- [ ] **Answer quality:** all four Ragas metrics (faithfulness, answer relevancy, context
      precision, context recall) on all 60 answerable items if the free budget allows,
      otherwise a documented stratified sample of at least 30, n stated per metric.
      Context recall runs on v2 only, after the golden item review.
- [ ] **Refusal:** refusal rate on the 8 existing refusal/clarification items plus at least 15
      new out-of-scope probes; false-refusal rate on answerable items. Validation refusals
      and evidence refusals counted separately.
- [ ] **Latency:** p50, p95, p99 for validate, retrieve and rerank over at least 1,000 requests
      (no LLM). End to end and generation: p50 and p95 over at least 50 requests (no p99 at
      that n). Hardware stated.
- [ ] **From the same load run:** tokens per request, estimated cost per request (price page
      and date cited, labelled estimated), citation coverage, failure rate.
- [ ] **Docling tables:** table subset and overall numbers on v1 and v2 against the PyMuPDF
      baseline; default-or-flag decision made by the rule written before the run (5F).
- [ ] **No quality targets on Ragas.** Every result below expectation has a written diagnosis.
      The only threshold is the CI gate.

## Engineering

- [ ] CI green on a clean clone: install from a real lock on one Python version, tests, lint
      and format check, deterministic retrieval gate on a committable fixture (D3). A
      deliberately broken branch shown to turn CI red.
- [ ] Tests cover the overlap rule, the numeric-header check and loading the prompt file.
- [ ] Prompts versioned in YAML; version in traces and eval results.
- [ ] Traces record retrieved and reranked IDs, prompt, response, tokens and per-stage latency,
      including requests refused by validation.
- [ ] One injected-failure postmortem in `docs/RUNBOOK.md`.
- [ ] No model output rendered as raw HTML; provider rate limits return 503 with
      `Retry-After`, not 502.
- [ ] `docker build` and run work from a clean clone with documented steps.
- [ ] **Public deployment (must-have, owner decision): on AWS**, with health check, rate limit
      and request cap, no secret exposure. Serves no PDFs: citations link out to arXiv or DOI
      pages. Open point: AWS sign-up asks for a payment card, which conflicts with rule 11
      ("no credit card"); to be verified from AWS's own pages and resolved with the owner
      before 5G.
- [ ] No secrets in the repo or its history; `.gitignore` covers `data/`, `venv/`, `.env`.
- [ ] Code licensed MIT. Papers are never committed.

## Documentation

- [ ] README, `docs/ARCHITECTURE.md`, ADRs for D1-D3, RRF k, judge and generator choice,
      Docling; `docs/GAPS.md`, `docs/CHANGES.md`, a walkthrough per workstream in
      `docs/walkthrough/`, `docs/RUNBOOK.md`.

## Understanding (5H, after the build)

- [ ] All 12 stages done. Each answer scored 0, 1 or 2; a stage passes when no basic or
      intermediate question scores 0. Gaps logged in `docs/INTERVIEW_GAPS.md`.
- [ ] Final mock interview of about 20 questions: at least 70% of the maximum score, and no 0
      on "what the repo actually does" questions.

## Owner decisions recorded at G1 (2026-11-18)

- D3 confirmed: CI gate is deterministic retrieval; Ragas runs offline or on a schedule.
- Generator and judge on separate free budgets. Judge candidate: NVIDIA NIM. Generator: a
  different free provider. Candidates to check: Groq (other models), Gemini, OpenRouter,
  Cerebras, Mistral. Every limit verified from official docs with page and date (rule 11).
- 5A also fixes H2 (HTML injection) and M1 (rate-limit handling).
- The retrieval comparison ladder runs first in 5B, before any LLM spend.

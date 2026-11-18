# Gaps

Running list of gaps found beyond the brief. Severity: High, Medium, Low.
Status: open, fixed (with commit), limitation (documented, not fixed).
Source: workstream 0 audit, 2026-11-14 (see `docs/CHANGES.md`).

| ID | Sev | Gap | Evidence | Workstream | Status |
|---|---|---|---|---|---|
| H1 | High | CI has never passed: fails at `pip install` | GitHub Actions runs 43467098245, 43272484945 and earlier; `requirements.txt:134-139` ranges; CI Python 3.11 vs local 3.14 | 5A | fixed on branch; first CI run pending (S3) |
| H2 | High | LLM answer rendered as raw HTML in the UI | `frontend/streamlit_app.py:51` (`unsafe_allow_html=True` with `data['answer']`) | 5A | fixed on branch |
| H3 | High | Eval collects answers at a config that is not served; saved answers stale and unlabelled | `eval/collect_answer_runs.py:119` (50/12 vs API 20/6); `eval/answer_runs.jsonl` dated 2026-11-03, before the 11-12 rebuild | 5B | fixed on `ws/5b-eval-2`: collector uses served 20/6 and records model, prompt, k, dataset hash |
| H4 | High | Reranker benefit unknown; hybrid@6 never measured | `eval/baseline_before_docling.json`: reranked@6 page hit 0.80 vs hybrid@20 0.933 (different k) | 5B ladder | measured 2026-11-19: rerank@6 2 gained / 4 lost (p=0.69), MRR CI includes 0; no evidence of benefit. Decision deferred to v2 + answer quality + latency |
| M1 | Med | Any provider error (incl. 429) retried without JSON mode, doubling calls; quota errors returned as 502 | `app/core/generation.py:51-63`; `app/api/routes.py` 502 on `GenerationError` | 5A | fixed on branch |
| M2 | Med | Positional chunk IDs renumber on any rebuild | `app/core/chunking.py:45` (`{doc_id}_c{idx:04d}`) | 5F | open |
| M3 | Med | Validation and evidence refusals share one flag; validation refusals not traced | `app/api/routes.py` (`answer`, early return before `answer_trace`) | 5B/5D | open |
| M4 | Med | Langfuse defaults to enabled in code, disabled in `.env.example` | `app/core/observability.py:58` | 5D | open |
| M5 | Med | Ragas output drops refused rows silently and records no judge, model, n or date | `eval/run_ragas.py` (row filter; output payload) | 5B | fixed on `ws/5b-eval-2`: per-record judge, embedding, generator, prompt, dataset hash, calls, tokens; refused items listed |
| M6 | Med | Doc hit inflated: 33/60 answerable questions name an acronym or method (rough regex) | audit command, 2026-11-14 | 5B review | measured on v2: 6 unnamed paraphrases all found the right paper at rank 1 (wording bias: written from the evidence sentence) |
| M7 | Med | No lint or format configuration; no lint in CI | no `pyproject.toml`, `setup.cfg` or ruff config | 5E | open |
| M8 | Med | No licence; `/papers` serves every PDF; doc IDs are raw filenames | GitHub API `license: null`; `app/api/routes.py` `open_paper` | 5A (licence), 5G | licence fixed (MIT); PDF serving open (5G) |
| M9 | Med | Overlap rule and numeric-header check have no tests | `tests/test_extract.py` has 2 regex tests only | 5A | fixed on branch |
| M10 | Med | 155 of 178 detected tables (87%) flagged suspicious; only 23 usable | audit count over `data/extracted_structured`, 2026-11-14 | 5F | open |
| L1 | Low | RRF `k=10` with no recorded reason | `app/core/retrieval.py:59,97` | 5B ladder / ADR | open |
| L2 | Low | Unused deps (`groq`, `pdfplumber`), unused `DEFAULT_MODEL` and `os` import, dead `extract_figures`, 3 empty files | grep; `git ls-files` | 5A | fixed on branch |
| L3 | Low | `scripts/audit_overlap.py` copies `overlap_fraction`; label "currently deleted" is wrong after the fix | `scripts/audit_overlap.py` | 5A | fixed on branch |
| L4 | Low | Third-party skill files untracked and not ignored | `.agents/`, `.claude/`, `skills-lock.json` | 5A | fixed on branch |
| L5 | Low | Stale worktree and `claude-audit` branch | `git worktree list`, `git branch` | owner | open |
| L6 | Low | 24,000-character context cap can drop reranked chunks while their IDs stay valid | `app/core/generation.py:22` | 5C | open |
| L7 | Low | GitHub description and topics empty | GitHub API | owner (G5) | open |
| S1 | High | Schedule: about 12.5 working days of planned work against an end date of 2026-11-19 | `docs/DEFINITION_OF_DONE.md` | owner | closed 2026-11-18: owner dropped the cut-off; scope not cut for a date |
| S2 | Med | Deployment on AWS conflicts with rule 11 if sign-up needs a card | rule 11; to verify on AWS pages before 5G | 5G / owner | resolved 2026-11-18: rule 11 amended (AWS free trial, billing alarm, budget cap); terms verified before 5G |
| S3 | Med | scikit-network 0.33.5 has no Linux cp314 wheel; CI builds it from source, unproven until the first run | PyPI file list for scikit-network 0.33.5 | 5A | resolved: CI run on 548832a passed (2026-11-18) |
| S4 | Low | OpenAI SDK retries 429s up to 2 times by default before our handler sees them | openai SDK default `max_retries=2` | 5B | open |
| S5 | Med | If `RAGAS_API_KEY` is set but `RAGAS_BASE_URL` is empty, `run_ragas.py` sends the judge key to the generator's base URL (Groq) | `eval/run_ragas.py` (`base_url=os.getenv("RAGAS_BASE_URL") or llm_settings.base_url`) | 5B | fixed on `ws/5b-eval-2`: run_ragas refuses a partial RAGAS_* configuration |
| S6 | Low | Unknown whether Langfuse merges or replaces metadata across `trace.update` calls; prompt version is therefore also written to the trace output | `app/api/routes.py` | 5D | open |
| S7 | Med | Query expansion rules fire on only 1 of 60 golden questions (G07); their effect is unmeasured, and they are corpus-tuned | ladder results 2026-11-19 (`questions_changed_by_expansion`) | 5B v2 | partly addressed: v2 adds 4 expansion-trigger items; expansion improved first page rank for G125 (3->2) and G126 (3->1) |
| S8 | Low | Ladder p-values are uncorrected for 10 comparisons; none survives Bonferroni (0.005) | `eval/results/ladder_golden_v1_2026-11-19.md` | 5B | documented as a caveat |
| S9 | High | Table questions are at the retrieval ceiling (hybrid@6 page hit 26/26 on v2), so the 5F rule "Docling default only if the table subset improves" on retrieval cannot show a gain | `eval/results/ladder_subsets_golden_v2_2026-11-19.md` | 5F / owner (G6) | open: proposal to add an answer-level table metric (exact required numbers in the answer) |
| S10 | Med | Selection bias: the 14 new structured-table questions were written from tables PyMuPDF detected; missed (booktabs) tables are covered only by 6 body-text items | `eval/GOLDEN_REVIEW.md` | 5F | open: add questions on missed tables before the Docling comparison |
| S11 | Low | v1 page hit understates retrieval: 2 of the 4 baseline page misses (G03, G26) were label errors | `eval/GOLDEN_REVIEW.md` | 5B | fixed in v2 (v1 frozen) |
| S12 | Low | `ollama --version` auto-starts the Ollama app and server on this laptop (started and then stopped by the assistant on 2026-11-19) | process list | note | closed |
| S13 | Med | A Docker container on the owner's laptop also listens on port 8000; a health check hit it before Cited had started | pilot 2026-11-19: response with `resume_uploaded`, `telegram_configured`; `Get-NetTCPConnection -LocalPort 8000` | 5G | open: local runs use port 8765 and verify `/health` reports 2,771 chunks |
| S14 | Med | Answer relevancy penalizes terse, correct numeric answers (G106 "88.43%" scored 0.49) | `eval/results/ragas_pilot_2026-11-19.md` | 5B | open: report answer relevancy separately for numeric items |
| S15 | Med | The generator adds facts from its own knowledge ("NT-Xent" in G09 is in none of the 6 retrieved chunks), against the prompt rule | pilot, checked by hand | 5B / answer_v2 | open: measure how often in the full run before changing the prompt |
| S16 | Med | NIM credit balance and daily cap are unknown; a full run needs about 1.94M judge tokens | pilot sizing | 5B | open: run is resumable, so a credit stop loses nothing |
| S17 | Low | Rate-limit parser read "60ms" as 60 minutes | pilot 2026-11-19 | 5B | fixed (commit 51e3057) |

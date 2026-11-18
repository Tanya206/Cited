# Gaps

Running list of gaps found beyond the brief. Severity: High, Medium, Low.
Status: open, fixed (with commit), limitation (documented, not fixed).
Source: workstream 0 audit, 2026-11-14 (see `docs/CHANGES.md`).

| ID | Sev | Gap | Evidence | Workstream | Status |
|---|---|---|---|---|---|
| H1 | High | CI has never passed: fails at `pip install` | GitHub Actions runs 43467098245, 43272484945 and earlier; `requirements.txt:134-139` ranges; CI Python 3.11 vs local 3.14 | 5A | fixed on branch; first CI run pending (S3) |
| H2 | High | LLM answer rendered as raw HTML in the UI | `frontend/streamlit_app.py:51` (`unsafe_allow_html=True` with `data['answer']`) | 5A | fixed on branch |
| H3 | High | Eval collects answers at a config that is not served; saved answers stale and unlabelled | `eval/collect_answer_runs.py:119` (50/12 vs API 20/6); `eval/answer_runs.jsonl` dated 2026-11-03, before the 11-12 rebuild | 5B | open |
| H4 | High | Reranker benefit unknown; hybrid@6 never measured | `eval/baseline_before_docling.json`: reranked@6 page hit 0.80 vs hybrid@20 0.933 (different k) | 5B ladder | open |
| M1 | Med | Any provider error (incl. 429) retried without JSON mode, doubling calls; quota errors returned as 502 | `app/core/generation.py:51-63`; `app/api/routes.py` 502 on `GenerationError` | 5A | fixed on branch |
| M2 | Med | Positional chunk IDs renumber on any rebuild | `app/core/chunking.py:45` (`{doc_id}_c{idx:04d}`) | 5F | open |
| M3 | Med | Validation and evidence refusals share one flag; validation refusals not traced | `app/api/routes.py` (`answer`, early return before `answer_trace`) | 5B/5D | open |
| M4 | Med | Langfuse defaults to enabled in code, disabled in `.env.example` | `app/core/observability.py:58` | 5D | open |
| M5 | Med | Ragas output drops refused rows silently and records no judge, model, n or date | `eval/run_ragas.py` (row filter; output payload) | 5B | open |
| M6 | Med | Doc hit inflated: 33/60 answerable questions name an acronym or method (rough regex) | audit command, 2026-11-14 | 5B review | open |
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

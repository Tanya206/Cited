# Changes

Append-only log. One entry per approved change, newest at the bottom.
Each entry: date, what changed, why, how it was verified, numbers before and after,
alternatives rejected. Numbers are only those produced by a command that was actually run.

---

## 2026-11-13: Workstream 0 audit (read-only, no files changed)

**What:** audit of the local repo and the published GitHub state against `CLAUDE.md`.

**Verified (command or source in brackets):**
- `python -m pytest -q`: 18 passed (local venv, Python 3.14.6).
- `python -m eval.validate_golden`: 68 items, 0 structural errors, 0 pending evidence.
  Split: 60 answer, 7 refusal, 1 clarification (read from `eval/golden_dataset.json`).
- Git history key scan (`git log --all -S` for `gsk_`, `sk-`, `sk-lf-`, `pk-lf-`, `AIza`, `hf_`):
  no keys. The single `sk-` hit is the word "hyperparam-eter" in `eval/EVIDENCE_REVIEW.md`.
- Extraction fixes are present in `app/ingestion/extract.py`: Roman-numeral captions
  (`CAPTION_RE`, `parse_caption_number`), overlap rule (`overlap_fraction`,
  `TABLE_BLOCK_INSIDE_RATIO = 0.8`, only non-suspicious tables remove body text),
  `header_is_numeric` check.
- Reranked retrieval numbers, computed from `eval/baseline_before_docling.json` (n=60,
  hybrid top 20 reranked to top 6, file dated 2026-11-12): doc hit 0.95, page hit 0.80,
  doc MRR 0.8283, page MRR 0.5419. Hybrid top 20 for comparison: page hit 0.9333.
  This is not a like-for-like comparison (k=20 vs k=6); hybrid@6 has not been measured.

**Disagreements with the brief or docs:**
- GitHub Actions has failed on every run checked (Sept to 12 Nov). It fails at
  `pip install -r requirements.txt`, so pytest never runs in CI. Probable cause (not confirmed,
  log needs auth): CI uses Python 3.11, local venv is 3.14, pins resolved on 3.14.
- `requirements.txt` is not a full lock: it contains ranges (ragas, langfuse, streamlit,
  pytest, openai).
- `eval.validate_golden` always reads `data/chunks.jsonl`, which CI does not have.
  `docs/EVALUATION.md` says CI runs it without the corpus; that is not true.
- `eval/answer_runs.jsonl` (60 answers, 3 Nov) and `eval/ragas_results.json` (5 items, 5 Nov)
  exist locally but predate the 12 Nov rebuild and record no model, prompt or config. Not citable.
- `eval/collect_answer_runs.py` calls `/answer` with `retrieve_k=50, rerank_k=12`;
  the API default and the baseline use 20 / 6.
- Recent commits went directly to `main`.
- GitHub repo: public, no description, no topics, no licence.

**Not in the brief:** RRF uses `k=10` (not the common 60) with no recorded reason;
`_request_payload` retries on any exception including HTTP 429 and the API returns 502 for
provider errors; Langfuse defaults to enabled in code but disabled in `.env.example`;
validation refusals and evidence refusals share one `refused` flag; `groq` and `pdfplumber`
are pinned but never imported; empty `Dockerfile`, `docker-compose.yml`,
`app/ingestion/ingest.py`; `extract_figures` is unused; a stale worktree
`Cited.worktrees/update-extract-py-table-extraction-logic` exists.

**Hardware (for local-model decisions):** AMD Ryzen 7 7735U, about 16 GB RAM (15.2 GB usable),
integrated AMD Radeon graphics, no CUDA GPU.

---

## 2026-11-13: Session protocol (branch `chore/session-protocol`)

**What:** added this file and `docs/STATUS.md`; added `CLAUDE.md` to `.gitignore`.

**Why:** `CLAUDE.md` requires a change log and it did not exist; the audit findings existed only
in a chat transcript. `STATUS.md` holds the current state and next step so any session can
resume from it. `CLAUDE.md` contains the owner's personal background and stays out of the
public repo.

**Verified:** `git diff main --stat` shows only `.gitignore`, `docs/CHANGES.md`,
`docs/STATUS.md`; `python -m pytest -q` unchanged (18 passed).

**Numbers:** none affected. Docs only.

**Alternatives rejected:** keeping handoff notes in `CLAUDE.md` (it is the brief, not a log,
and it is not committed); GitHub Issues or a project board (extra overhead, and the assistant
cannot write to GitHub).

---

## 2026-11-14: Workstream 0 re-audit against the revised CLAUDE.md (read-only)

**Verified (commands run 2026-11-14):**
- `python -m pytest -q`: 18 passed. `python -m eval.validate_golden`: 68 items, 0 errors, 0 pending.
- Key scan over all revisions (10 prefixes plus a key-shape regex): no keys. The only prefix
  hits are the pattern names written in this file on 2026-11-13. `.env` never committed.
- Section 4 claims confirmed from `data/`: 14 captions in `2007.09990v1`; 16 of 44 papers detect
  zero tables; 2,771 chunks (2,209 body, 538 caption, 24 table); 8 tables flagged only by
  `header_is_numeric`, 4 of them DEC (`1511.06335v2`); overlap fix at `extract.py:450-459`.
- New fact: PyMuPDF detected 178 tables, 155 (87%) flagged suspicious, 23 usable.
- Not verifiable: SimCLR +970 words and the 38 deleted blocks (no pre-fix extraction saved).
- CI still fails at `pip install`, including on merged PR #4 (run 43467098245).

Full gap list with evidence: `docs/GAPS.md`.

## 2026-11-18: G1 ratified

The owner ratified the Definition of Done (`docs/DEFINITION_OF_DONE.md`) with two additions:
H2 and M1 are fixed inside 5A, and the retrieval comparison ladder runs first in 5B.
Owner answers: end date 2026-11-19; hardware Ryzen 7 7735U, about 16 GB RAM, no CUDA GPU;
D3 confirmed; public deployment on AWS is must-have; no PDFs served publicly; rederive skill
files ignored; NVIDIA NIM as judge candidate with a different free provider for the generator;
MIT licence for the code.

---

## 2026-11-18: Workstream 5A, hygiene (branch `ws/5a-hygiene`)

Walkthrough with commands: `docs/walkthrough/5a-hygiene.md`.

### Decision: one Python version (3.14) and a real lock file (fixes H1)
- **Problem:** every CI run failed at install. Reproduced with a Linux/3.11 pip dry run:
  `No matching distribution found for numpy==2.5.2` (numpy 2.5 has no 3.11 wheels). The old
  `requirements.txt` differed from the working venv on 39 versions, lacked 41 installed
  packages, had ranges for 5 direct deps, and never declared PyStemmer (imported at
  `app/core/bm25_index.py:12`). `pip check` in the venv: Pillow 13.0.0 and pyarrow 26.0.0
  violate streamlit 1.65 (`<13`, `<26`).
- **Options:** (a) CI on 3.14 with a lock frozen from the tested venv; (b) move local and CI
  to 3.13, where every package has wheels, and re-resolve; (c) keep 3.11 in CI and re-resolve
  older versions. (c) means testing a different environment than the one we run; (b) costs a
  new venv and a re-test of everything on the last day before the end date.
- **Decision:** (a). Lock = `pip freeze` of the venv minus unused `groq`, `pdfplumber`,
  `pdfminer.six`, `pypdfium2`, `cryptography`, `cffi`, `pycparser`, plus `watchfiles` (needed
  on Linux). Pillow 12.3.0 and pyarrow 25.0.1. CPU-only torch in CI via the PyTorch index.
- **Verification:** `pip check` -> "No broken requirements found". Lock equals venv for all
  163 pins. Linux/CPython 3.14 dry-run resolution succeeds; everything except scikit-network
  has a cp314 wheel. Unused packages uninstalled from the venv; all modules still import and
  the tests pass.
- **Invalidates:** nothing measured. **Risk:** scikit-network 0.33.5 builds from source in
  CI; unproven until the first run after push. Fallback: option (b).

### Decision: golden validator `--structure-only` for CI
- **Problem:** `eval/validate_golden.py` always read `data/chunks.jsonl`, absent in CI.
- **Options:** drop the CI step; skip silently when the file is missing; explicit flag.
  A silent skip would hide a misconfigured local run, so: explicit flag.
- **Verification:** both modes report 68 items, 0 errors; 4 new tests (duplicate ID,
  evidence outside expected pages, empty quote, valid file). A clean export of the branch with
  no `data/` folder: 34 passed, structure check 0 errors.

### Decision: escape model output in the UI (fixes H2)
- **Problem:** `frontend/streamlit_app.py:51` rendered the answer with `unsafe_allow_html=True`.
- **Options:** drop the styled card and use plain `st.markdown` (Markdown still renders links
  and images from model output); escape into the card. Escaping keeps the design and renders
  nothing from the model.
- **Verification:** `tests/test_render.py` runs the real app with
  `<img src=x onerror="alert(1)">` as the answer; the card contains `&lt;img ...` as text.

### Decision: retry only JSON-mode rejections; 503 + Retry-After on 429 (fixes M1)
- **Problem:** `generation.py` retried any exception without JSON mode. Measured on `main`
  with a scripted 429: 2 provider calls and the error "failed after a JSON retry"; API 502.
- **Options:** keep one broad retry; retry only HTTP 400 and map 429 to 503. Only a 400 means
  JSON mode was rejected; retrying a 429 or 5xx cannot help.
- **Verification:** 5 tests in `tests/test_provider_errors.py`: 429 -> 1 call and
  `retry_after=7`; 400 -> second call without `response_format`; 500 -> 1 call; API 503 with
  `Retry-After: 7` and the provider message in the body (parsed by
  `eval/collect_answer_runs.py`); other failures 502.
- Note: the OpenAI SDK itself still retries 429s up to 2 times by default. Revisit in 5B when
  the provider is chosen.

### Decision: tests for the extraction fixes (M9)
- Moved the block filter and the header check into `remove_table_blocks` and
  `is_header_numeric`. **Verification of no behaviour change:** all 44 papers re-extracted
  into a scratch folder; JSON identical to `data/extracted_structured` (crop paths aside).
  Indexes not touched (no G3). Mutation check: restoring "any table deletes text" fails
  `test_suspicious_table_never_removes_body_text`.

### Other changes
- Removed empty `Dockerfile`, `docker-compose.yml`, `app/ingestion/ingest.py`; dead
  `extract_figures`; unused `DEFAULT_MODEL` and `os` import.
- `scripts/audit_overlap.py` imports `overlap_fraction` from `extract.py`; reports 30
  partially overlapping blocks, all kept in the body.
- MIT `LICENSE`. `.gitignore`: `.agents/`, `.claude/`, `skills-lock.json`.
- README install line uses the lock.

**Numbers:** tests 18 -> 34 passed. `pip check` 2 conflicts -> 0. Retrieval baseline
unchanged (no index rebuilt).

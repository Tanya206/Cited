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

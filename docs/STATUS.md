# Status

Rewritten at the end of every session. Read this first, then the last entries of
`docs/CHANGES.md`.

**Last updated:** 2026-11-13
**Working branch:** `chore/session-protocol` (not yet pushed or merged)

## Next step

Phase 1, "clean the ground" (workstream 5A). First proposal: make CI pass on a clean
checkout. Pick one Python version for local and CI, generate a real lock file on it, and make
the golden-validation step not depend on `data/`. Then remove empty and unused files and
dependencies.

## Agreed plan

1. Clean the ground: CI green, hygiene, DoD saved (about 1 day).
2. Ablation ladder, retrieval only, no LLM calls, each step paired with a learning session:
   vector only, BM25 only, hybrid RRF, + query expansion, + rerank compared at the same k
   (about 3 days).
3. Add at least 10 table questions, then Docling tables as extra chunks on their own branch,
   measured as one ablation step (about 2 days). Needs an ADR amending D1's ordering.
4. Prompt versioning (5C), then answer quality with Ragas (5B), including faithfulness with and
   without rerank on a small sample (about 2.5 days).
5. Observability, CI quality gate, deployment, README (about 6 days).

## Session end checklist

- `git status` clean on the session branch; scratch files outside the repo.
- `python -m pytest -q` passes.
- One commit per approved change, message says what and why.
- `docs/CHANGES.md` entry per change; this file rewritten.
- Owner reviews the diff and pushes. The assistant does not push (CLAUDE.md rule 3).

## Open decisions

- Definition of Done not ratified. Open points: quality targets vs measurement only, Ragas
  sample size, which Ragas metrics, out-of-scope refusal probes, latency method (p99 only for
  retrieve and rerank), D3 CI gate and tolerance, whether a public deployment is must-have,
  PDF policy for the demo (recommended: link out to arXiv or DOI, serve no PDFs), scoring
  rubric for the understanding criteria.
- Target date for applications (sets what can be cut).

## Known state

- Local: 18 tests pass, golden set valid (68 items).
- CI: failing at dependency install on every run.
- Saved answer runs and Ragas results are stale (before the 2026-11-12 rebuild).

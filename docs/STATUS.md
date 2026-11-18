# Status

Rewritten at the end of every session. Read this first, then the last entries of
`docs/CHANGES.md` and `docs/GAPS.md`.

**Last updated:** 2026-11-18
**Working branch:** `ws/5a-hygiene` (complete, committed, not pushed)
**Hard end date:** 2026-11-19 (`docs/DEFINITION_OF_DONE.md`)

## Next step

1. Owner: review and push `ws/5a-hygiene`, open the PR, and watch the first CI run. If it
   fails at building scikit-network, the fallback is Python 3.13 locally and in CI (S3).
2. Owner decision needed: scope for the remaining time (gap S1). About 11.5 working days of
   planned work remain and the end date is tomorrow.
3. Then 5C (prompt YAML) on `ws/5c-prompts`, followed by 5B starting with the retrieval
   comparison ladder (no LLM spend).

## Done

- Workstream 0 audit, G1 ratified (2026-11-18).
- 5A: lock file and CI on Python 3.14, golden structure check without `data/`, H2 (HTML
  escaping), M1 (429 handling), tests for the extraction fixes, dead code and empty files
  removed, MIT licence. Tests: 34 passed, locally and in a clean export without `data/`.

## Not verified

- CI on GitHub (runs only after the push).
- scikit-network building from source on Linux / Python 3.14.

## Open decisions

- S1: what to cut for the 2026-11-19 end date.
- S2: AWS sign-up asks for a payment card, which conflicts with rule 11. Verify on AWS pages
  and decide before 5G.

## Session end checklist

- `git status` clean on the session branch; scratch files outside the repo.
- `python -m pytest -q` passes.
- One commit per change; `docs/CHANGES.md`, `docs/GAPS.md` and this file updated.
- Owner reviews the diff and pushes (CLAUDE.md rule 3).

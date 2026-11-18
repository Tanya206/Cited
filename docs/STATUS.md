# Status

Rewritten at the end of every session. Read this first, then the last entries of
`docs/CHANGES.md` and `docs/GAPS.md`.

**Last updated:** 2026-11-18
**Working branch:** `ws/5c-prompts` (complete, committed, not pushed)
**End date:** none fixed. Re-estimate from measured pace after the retrieval ladder.

## Next step

1. Owner: review and push `ws/5c-prompts`, open the PR, merge when CI is green.
2. Owner: set the three judge variables in `.env` together (gap S5): `RAGAS_API_KEY`,
   `RAGAS_BASE_URL=https://integrate.api.nvidia.com/v1`, and `RAGAS_MODEL` once the judge is
   picked. Check credit balance and per-model rate limit on build.nvidia.com (TODO(owner)).
3. Assistant: 5B on `ws/5b-eval`, starting with the retrieval comparison ladder (vector, BM25,
   hybrid, + expansion, + rerank; k=6 and k=20; golden v1; no LLM calls). Then re-estimate the
   remaining work and give a date.

## Done

- Workstream 0, G1 (2026-11-18).
- 5A (merged as PR #5, first green CI on 548832a).
- 5C: prompt in `prompts/answer_v1.yaml`, byte-identical to the old f-strings; version and hash
  in responses, traces, answer runs and Ragas results. 46 tests pass.

## Measured pace

| Workstream | Estimate | Measured (assistant wall-clock) |
|---|---|---|
| 5A | 1 day | 29 min (14:37-15:06) |
| 5C | 0.5 day | about 15 min (16:40-16:55), plus NVIDIA research |

## Not verified

- CI for `ws/5c-prompts` (runs after the push).
- Whether Langfuse merges metadata across updates (S6); version is also written to the output.

## Session end checklist

- `git status` clean on the session branch; scratch files outside the repo.
- `python -m pytest -q` passes.
- One commit per change; `docs/CHANGES.md`, `docs/GAPS.md` and this file updated.
- Owner reviews the diff and pushes (CLAUDE.md rule 3).

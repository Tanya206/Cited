# Status

Rewritten at the end of every session. Read this first, then the last entries of
`docs/CHANGES.md` and `docs/GAPS.md`.

**Last updated:** 2026-11-19
**Working branch:** `ws/5b-eval` (part 1 committed, not pushed; 5B continues on this branch)
**Estimated build completion:** Tuesday 2026-11-24 (range: Sunday 22 to Wednesday 25 Nov;
see the re-estimate below)

## Next step

1. Owner: review and push `ws/5b-eval` (part 1), open the PR, merge when CI is green.
2. Assistant, 5B part 2, in this order:
   a. Golden review of the 60 v1 items into `eval/GOLDEN_REVIEW.md`; create `golden_v2`.
   b. At least 20 table questions in v2, plus questions that trigger query expansion (S7).
   c. Generator provider survey (one free provider allowed behind a public demo).
   d. Resumable judge step; fix S5 (judge key sent to the generator URL).
   e. 5-item pilot with the NIM judge (G2: tokens estimated first).
3. Owner: spot-check at least 10 golden fixes; approve the pilot (G2).

## Done

- Workstream 0, G1; 5A (PR #5); 5C (PR #6).
- 5B part 1: golden v1 frozen; retrieval ladder on v1 (results in `eval/results/`).

## Measured pace (assistant wall-clock, from git)

| Work | Original estimate | Measured |
|---|---|---|
| 5A | 1 day | 29 min |
| 5C | 0.5 day | about 15 min |
| 5B part 1 (ladder) | part of 3 days | 12 min |

## Re-estimate of the remaining work

Code and reading work has run 15 to 30 times faster than the day-based estimates. The
remaining work is mostly limited by things that pace does not change: owner reviews, gates,
provider quotas and unmeasured compute. Agent times below are estimates scaled from the
measured pace; the other limits are listed separately.

| Work | Assistant time (estimate) | What actually limits it |
|---|---|---|
| 5B golden review (60 items) and v2 | 1-2 h | owner spot-check of 10+ fixes |
| 5B 20+ table questions | 1-2 h | none |
| 5B provider survey, resumable judge, S5 fix | 1-1.5 h | none |
| 5B pilot, then full Ragas and refusal scoring | 0.5-1 h | G2 approval; NIM 40 RPM; generator daily quota (unknown; Groq's daily limit blocked the last run) |
| 5D observability, load run, runbook | 2-3 h | generation requests use quota |
| 5F Docling | 1-2 h | Docling CPU time not yet measured; G2 model download; G3 rebuild (27 min on 2026-11-12) |
| 5E CI gate, lint, red-build proof | 1-2 h | owner push to show the red build |
| 5G Docker and AWS | 3-4 h | Docker image build; AWS steps need the owner (G5) |
| 5I README and docs | 1-2 h | final numbers |

Total assistant time: about 12-20 hours. Calendar estimate, assuming one owner review sitting
per day: 5B part 2 on 19-20 Nov, 5D and 5F on 21 Nov, 5E and 5G on 22-23 Nov, 5I on 24 Nov.
**Most likely completion: Tuesday 2026-11-24.** Earliest: Sunday 22 Nov, if quotas and Docling
cooperate. It slips day for day if the generator's daily quota stops the Ragas run or Docling
on CPU takes hours. Both are measured early (pilot, one-paper Docling timing) so a slip shows
up quickly.

## Not verified

- CI for `ws/5b-eval` (runs after the push).
- Generator daily quota (Groq or replacement) and NIM credit balance.

## Session end checklist

- `git status` clean on the session branch; scratch files outside the repo.
- `python -m pytest -q` passes.
- One commit per change; `docs/CHANGES.md`, `docs/GAPS.md` and this file updated.
- Owner reviews the diff and pushes (CLAUDE.md rule 3).

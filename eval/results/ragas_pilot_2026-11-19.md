# Ragas pilot, 2026-11-19 (gate G2, 5 items)

Items: G09, G27, G33, G60, G106 from `eval/golden_v2.json`. Generator: Groq `openai/gpt-oss-20b`,
prompt `answer_v1`, served configuration (20 retrieved, 6 reranked). Judges on NVIDIA NIM.
Embedding for answer relevancy: local `BAAI/bge-small-en-v1.5`. Ragas 0.3.9. Per-record data:
`ragas_pilot_nemotron-3-ultra_2026-11-19.jsonl`, `ragas_pilot_gemma-4-31b_2026-11-19.jsonl`,
`judge_latency_probe_2026-11-19.json`. The answers themselves are in `eval/answer_runs_v2.jsonl`,
not committed because they contain excerpts of the papers.

**n=5. These are pilot numbers for sizing and judge choice, not quality results.**

## Generator cost (measured from provider usage)

| Item | Prompt | Output | of which reasoning | Total | Calls |
|---|---|---|---|---|---|
| G09 | 2,659 | 371 | 225 | 3,030 | 1 |
| G27 | 2,432 | 549 | 376 | 2,981 | 1 |
| G33 | 2,448 | 330 | 239 | 2,778 | 1 |
| G60 | 2,290 | 211 | 145 | 2,501 | 1 |
| G106 | 2,676 | 185 | 152 | 2,861 | 1 |
| Mean | 2,501 | 329 | 227 (69% of output) | **2,830** | 1 (no repair calls) |

## Judge choice

`mistralai/mistral-large-4-1t-a52b` (the first choice) timed out: the first metric did not finish
within Ragas's 180 s limit. A one-request probe of six NIM models (same prompt: G09's answer and
first context, JSON output, 1,200-token cap; n=1 each, shared free tier, so latency is noisy):

| Model | Seconds | Output tokens | Valid JSON |
|---|---|---|---|
| mistral-large-4-1t-a52b | 37.4 | 1,200 (cap) | no |
| nemotron-3-ultra-550b-a55b | 11.3 | 1,200 (cap) | no |
| kimi-k3.1-pro | timed out (180 s) | - | - |
| gemma-4-31b-it | 43.6 | 412 | yes |
| glm-5.3-flash | timed out (180 s) | - | - |
| nemotron-3.5-lightning-30b-a3b | 7.0 | 1,200 (cap) | no |

Re-run of nemotron-3-ultra with 4,096 output tokens (the Ragas setting): 15.9 s, 1,711 output
tokens, reasoning returned in a separate field, valid JSON. The 1,200 cap was the cause.

Head-to-head on faithfulness (same 5 answers):

| Item | nemotron-3-ultra | gemma-4-31b |
|---|---|---|
| G09 | 0.857 | 0.857 |
| G27 | 1.000 | 1.000 |
| G33 | 1.000 | 1.000 |
| G60 | 1.000 | 1.000 |
| G106 | 1.000 | 1.000 |

Agreement 5/5, but 4 of 5 are at the ceiling, so this is weak evidence of judge quality. The one
informative item, G09, was checked by hand (below) and both judges were right.

**Recommendation: `nvidia/nemotron-3-ultra-550b-a55b` as the judge**, `gemma-4-31b-it` as the
second judge for an agreement check on a larger sample in the full run. Reasons: it completes
every metric, about 16 s per call versus about 40 s for gemma, and NIM limits requests per minute
rather than tokens. Cost: it spends more tokens on faithfulness (5,944 versus 3,984 per item)
because of its reasoning.

## Judge cost per item (nemotron-3-ultra, measured)

| Metric | Calls | Tokens (prompt + completion) |
|---|---|---|
| faithfulness | 2 | 5,944 (3,548 + 2,396) |
| context precision (no reference) | 6 (one per context) | 11,272 (8,259 + 3,013) |
| answer relevancy | 1 | 702 (434 + 269) |
| context recall | 1 | 3,586 (3,123 + 463) |
| **All four** | **10** | **21,504** |

Wall time: about 2 minutes per item with 2 workers.

## Pilot scores (nemotron-3-ultra)

| Item | Faithfulness | Context precision | Answer relevancy | Context recall |
|---|---|---|---|---|
| G09 | 0.857 | 1.000 | 0.938 | 1.000 |
| G27 | 1.000 | 1.000 | 0.719 | 1.000 |
| G33 | 1.000 | 0.833 | 0.985 | 1.000 |
| G60 | 1.000 | 1.000 | 0.993 | 1.000 |
| G106 | 1.000 | 0.250 | 0.493 | 1.000 |

## What the low scores mean (checked by hand)

- **G09 faithfulness 0.857:** the answer names the loss "NT-Xent", which appears in none of the 6
  retrieved chunks. The claim is true of the paper, but the model added it from its own
  knowledge, against the prompt rule "Do not use knowledge outside the evidence". Every other
  claim (four components, ResNet, throwing away the projection head) is in the chunks. Both
  judges flagged this.
- **G106 context precision 0.250:** correct. The answer "88.43%" is supported, but the only
  useful chunk (the table row) is at rank 4 of 6, and average precision is 1/4.
- **G106 answer relevancy 0.493:** an artefact. The metric generates a question from the answer
  and compares it with the real question; a bare number cannot reproduce the question. Terse,
  correct numeric answers are penalized. Read answer relevancy on numeric items with that in
  mind, or report it separately for them.

## Sizing the full run (90 answerable v2 items)

| Resource | Measured per item | 90 items | Limit | Consequence |
|---|---|---|---|---|
| Groq tokens | 2,830 | about 255K | 200K/day, 8K/min | about 1.3 days; about 2.8 answers per minute |
| NIM calls | 10 | 900 | 40/min | at least 23 minutes of calls; measured pace is about 3 hours |
| NIM tokens | 21,504 | about 1.94M | not published; credit balance not shown | unknown; the run is resumable, so a credit stop loses nothing |
| Second judge (faithfulness only, about 30 items) | 3,984 | about 120K | same | agreement check on a larger sample |

## Spend in this pilot

- Groq: 14,151 tokens (5 answers) plus one rejected request (429, tokens per minute).
- NIM: one timed-out run with mistral-large-4 (no score; tokens not reported), 7 probe
  requests (8,864 tokens: 6,518 for the six models plus 2,346 for the nemotron re-run), judge A
  107,522 tokens, judge B 19,920 tokens. About 136K tokens in total plus the timed-out run,
  slightly over the 120-130K estimate because of the probes.

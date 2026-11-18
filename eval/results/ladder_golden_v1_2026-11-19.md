# Retrieval comparison ladder, golden v1 (2026-11-19)

n=60 answerable items; pool 20 per retriever; RRF k=10; commit 68c2c6c; no LLM calls.

| Step | k | doc hit | page hit | doc MRR | page MRR |
|---|---|---|---|---|---|
| vector | 6 | 0.983 (59/60) | 0.683 (41/60) | 0.910 | 0.448 |
| vector | 20 | 0.983 (59/60) | 0.917 (55/60) | 0.910 | 0.468 |
| bm25 | 6 | 0.967 (58/60) | 0.700 (42/60) | 0.852 | 0.403 |
| bm25 | 20 | 0.983 (59/60) | 0.917 (55/60) | 0.853 | 0.428 |
| hybrid | 6 | 0.983 (59/60) | 0.833 (50/60) | 0.904 | 0.503 |
| hybrid | 20 | 1.000 (60/60) | 0.933 (56/60) | 0.906 | 0.512 |
| hybrid_expand | 6 | 0.983 (59/60) | 0.833 (50/60) | 0.904 | 0.503 |
| hybrid_expand | 20 | 1.000 (60/60) | 0.933 (56/60) | 0.906 | 0.512 |
| hybrid_expand_rerank | 6 | 0.950 (57/60) | 0.800 (48/60) | 0.828 | 0.542 |
| hybrid_expand_rerank | 20 | 1.000 (60/60) | 0.933 (56/60) | 0.833 | 0.542 |

## Paired comparisons (page level)

| Before -> after | k | page hits gained | lost | exact McNemar p | page MRR change [95% CI] |
|---|---|---|---|---|---|
| vector -> bm25 | 6 | 10 | 9 | 1.000 | -0.045 [-0.175, +0.087] |
| vector -> bm25 | 20 | 4 | 4 | 1.000 | -0.040 [-0.164, +0.083] |
| vector -> hybrid | 6 | 11 | 2 | 0.022 | +0.055 [-0.036, +0.148] |
| vector -> hybrid | 20 | 3 | 2 | 1.000 | +0.044 [-0.043, +0.134] |
| bm25 -> hybrid | 6 | 10 | 2 | 0.039 | +0.100 [+0.014, +0.184] |
| bm25 -> hybrid | 20 | 2 | 1 | 1.000 | +0.084 [+0.001, +0.166] |
| hybrid -> hybrid_expand | 6 | 0 | 0 | 1.000 | +0.000 [+0.000, +0.000] |
| hybrid -> hybrid_expand | 20 | 0 | 0 | 1.000 | +0.000 [+0.000, +0.000] |
| hybrid_expand -> hybrid_expand_rerank | 6 | 2 | 4 | 0.688 | +0.039 [-0.065, +0.143] |
| hybrid_expand -> hybrid_expand_rerank | 20 | 0 | 0 | 1.000 | +0.030 [-0.069, +0.129] |

Query expansion changed 1 of 60 questions (G07), so the hybrid -> hybrid_expand row measures almost nothing about expansion.

Categories with n <= 3 are in the JSON but not quoted here.

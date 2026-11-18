# Retrieval comparison ladder, golden_v2 (2026-11-19)

n=90 answerable items; pool 20 per retriever; RRF k=10; commit bb4cf42; no LLM calls.

| Step | k | doc hit | page hit | doc MRR | page MRR |
|---|---|---|---|---|---|
| vector | 6 | 0.989 (89/90) | 0.700 (63/90) | 0.918 | 0.433 |
| vector | 20 | 1.000 (90/90) | 0.933 (84/90) | 0.920 | 0.455 |
| bm25 | 6 | 0.967 (87/90) | 0.733 (66/90) | 0.885 | 0.465 |
| bm25 | 20 | 0.989 (89/90) | 0.900 (81/90) | 0.886 | 0.485 |
| hybrid | 6 | 0.989 (89/90) | 0.844 (76/90) | 0.920 | 0.506 |
| hybrid | 20 | 1.000 (90/90) | 0.933 (84/90) | 0.922 | 0.514 |
| hybrid_expand | 6 | 0.989 (89/90) | 0.844 (76/90) | 0.920 | 0.516 |
| hybrid_expand | 20 | 1.000 (90/90) | 0.933 (84/90) | 0.921 | 0.523 |
| hybrid_expand_rerank | 6 | 0.978 (88/90) | 0.822 (74/90) | 0.881 | 0.564 |
| hybrid_expand_rerank | 20 | 1.000 (90/90) | 0.933 (84/90) | 0.883 | 0.548 |

## Paired comparisons (page level)

| Before -> after | k | page hits gained | lost | exact McNemar p | page MRR change [95% CI] |
|---|---|---|---|---|---|
| vector -> bm25 | 6 | 14 | 11 | 0.690 | +0.032 [-0.067, +0.129] |
| vector -> bm25 | 20 | 3 | 6 | 0.508 | +0.029 [-0.063, +0.120] |
| vector -> hybrid | 6 | 15 | 2 | 0.002 | +0.073 [+0.011, +0.136] |
| vector -> hybrid | 20 | 2 | 2 | 1.000 | +0.059 [-0.001, +0.118] |
| bm25 -> hybrid | 6 | 12 | 2 | 0.013 | +0.041 [-0.025, +0.107] |
| bm25 -> hybrid | 20 | 4 | 1 | 0.375 | +0.029 [-0.034, +0.093] |
| hybrid -> hybrid_expand | 6 | 0 | 0 | 1.000 | +0.009 [+0.000, +0.026] |
| hybrid -> hybrid_expand | 20 | 0 | 0 | 1.000 | +0.009 [+0.000, +0.026] |
| hybrid_expand -> hybrid_expand_rerank | 6 | 3 | 5 | 0.727 | +0.048 [-0.035, +0.132] |
| hybrid_expand -> hybrid_expand_rerank | 20 | 0 | 0 | 1.000 | +0.025 [-0.054, +0.105] |

Query expansion changed 5 of 90 questions (G07, G124, G125, G126, G127); the hybrid -> hybrid_expand row can only move on those questions.

Categories with n <= 3 are in the JSON but not quoted here.

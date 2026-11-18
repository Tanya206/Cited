# Ladder subsets: golden_v2, commit bb4cf42

## Table questions (structured and body-text)

| Step @6 | page hit | doc hit | page MRR |
|---|---|---|---|
| vector | 21/26 (0.808) | 26/26 | 0.481 |
| bm25 | 23/26 (0.885) | 26/26 | 0.687 |
| hybrid | 26/26 (1.000) | 26/26 | 0.617 |
| hybrid_expand | 26/26 (1.000) | 26/26 | 0.617 |
| hybrid_expand_rerank | 25/26 (0.962) | 26/26 | 0.744 |

## Structured table chunks only

| Step @6 | page hit | doc hit | page MRR |
|---|---|---|---|
| vector | 16/20 (0.800) | 20/20 | 0.508 |
| bm25 | 18/20 (0.900) | 20/20 | 0.739 |
| hybrid | 20/20 (1.000) | 20/20 | 0.625 |
| hybrid_expand | 20/20 (1.000) | 20/20 | 0.625 |
| hybrid_expand_rerank | 19/20 (0.950) | 20/20 | 0.779 |

## Table values only in body/caption text

| Step @6 | page hit | doc hit | page MRR |
|---|---|---|---|
| vector | 5/6 (0.833) | 6/6 | 0.389 |
| bm25 | 5/6 (0.833) | 6/6 | 0.514 |
| hybrid | 6/6 (1.000) | 6/6 | 0.589 |
| hybrid_expand | 6/6 (1.000) | 6/6 | 0.589 |
| hybrid_expand_rerank | 6/6 (1.000) | 6/6 | 0.625 |

## Questions changed by query expansion (first labelled page rank @20)

| Item | hybrid | hybrid_expand |
|---|---|---|
| G07 | 1 | 1 |
| G124 | None | None |
| G125 | 3 | 2 |
| G126 | 3 | 1 |
| G127 | None | None |

## Named vs unnamed paraphrase (hybrid_expand_rerank @6)

| Named item | first doc rank | page hit | Unnamed item | first doc rank | page hit |
|---|---|---|---|---|---|
| G10 | 2 | True | G128 | 1 | True |
| G29 | 3 | True | G129 | 1 | True |
| G11 | 1 | False | G130 | 1 | True |
| G26 | 5 | False | G131 | 1 | False |
| G18 | 2 | True | G132 | 1 | True |
| G28 | 1 | True | G133 | 1 | True |

Small subsets: read these as case studies, not rates.

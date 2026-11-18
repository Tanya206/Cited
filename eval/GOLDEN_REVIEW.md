# Golden set review: v1 -> v2

Reviewed 2026-11-19 by claude-code. v1 (`eval/golden_v1.json`) is frozen and unchanged. Every
fix below is applied only in `eval/golden_v2.json` and is listed on the item as
`changed_in_v2`. Changed and new items carry `provenance.reviewed_by_owner: false` until the
owner checks them.

## How each item was reviewed

For all 60 answerable v1 items: the question, reference answer and evidence quotes were read
against the indexed chunk text. Checks: is the question clear; does the quote support every
claim in the reference answer; is the category right; are the expected pages complete (is the
answer also on an unlabelled page); does the question leak the answer. The 4 baseline page
misses were checked by searching every page of the expected paper. No LLM was used.

## Findings on existing items

| Item | Issue | Evidence | Fix in v2 |
|---|---|---|---|
| G01 | Question names no paper, but only FCN p1 counted; the aerial-segmentation paper (G58's source) defines the same thing on p1 | G58 quote: "Its aim is to determine, at every image pixel, the most likely class label..." | Both papers accepted (`expected_locations`), answer made source-neutral |
| G02 | Reference says FCNs replace fully connected layers with convolutions; the p1 quote does not say that | FCN p3 caption: "Transforming fully connected layers into convolution layers..." | p3 added to pages and evidence |
| G03 | Labelled p2 only; p1 abstract also answers it. One of the 4 baseline page misses: a label error, not a retrieval error | U-Net p1: "a symmetric expanding path that enables precise localization" | p1 added |
| G08 | Category `definition` but asks how the method works; quote covers negatives only | SimCLR p2: "maximizing agreement between differently augmented views" | category `method`; quote added |
| G18 | Reference says SLIC "adapts k-means"; not in the p1 evidence | p1 has no "k-means" | Reference trimmed to what the quote supports |
| G21 | "What is STEGO distilled from?" is grammatically wrong: STEGO distills features | question text | Reworded |
| G26 | Labelled p2 only; the p1 abstract answers it completely. Baseline page miss caused by the label | DeepCluster p1: "iteratively groups the features with ... k-means, and uses the subsequent assignments as supervision" | p1 added |
| G28 | Category `comparison` for a single-paper question | question text | category `method` |
| G37 | "More diverse, higher-fidelity" is supported only by the title on p1 | VQ-VAE-2 p1 title | p1 added |
| G52 | Category `definition` for a motivation question | question text | category `method` |
| G59 | Ambiguous: p8 has two tables. W-Net's SC ODS is 0.58 on BSDS300 (Table 1) and 0.57 on BSDS500 (Table 2). A correct "0.58" would have been marked wrong | PDF page 8 captions read directly with PyMuPDF | Question names BSDS500 |
| G41-G45 | Two-paper items: `expected_pages` is not tied to a paper, so a page number from the wrong paper counts as a page hit | `tests/test_retrieval_metrics.py::test_v1_scoring_lets_a_page_number_from_the_wrong_paper_count` | `expected_locations` (doc, page) pairs |
| G17, G38, G48 | Answerable from the paper title alone, so they test very little | reference answer equals or paraphrases the title | Kept; tagged `answer_in_title: true` |

Checked and left as they are:
- **G24 and G36** (the other 2 baseline page misses) are genuine retrieval misses. Their p1
  abstracts name the idea but do not contain the answer.
- **G40** (refusal: Potsdam mIoU) is valid: IIC and STEGO report Potsdam *accuracy*, and no
  indexed paper reports Potsdam mIoU. It is a hard near-miss.
- The other items: no issue found.

## Systemic issues

1. **Doc hit is inflated by method names.** 33 of 60 answerable questions contain an acronym or
   method name (rough regex). v2 adds 6 `unnamed_target` questions (G128-G133), each a
   paraphrase of an existing item without the method name (`variant_of`), so the effect can be
   measured on matched pairs.
2. **Query expansion was untested.** Its rules fired on 1 of 60 v1 questions. v2 adds 4
   questions that trigger it (G124-G127, `triggers_expansion: true`).
3. **Labels by one author.** The new items are written by claude-code, and the system under test
   is an LLM pipeline. Report the owner-reviewed subset separately.

## New items (33)

| IDs | Category | What they test |
|---|---|---|
| G101-G114 | `numeric_table` | Values in structured table chunks: single cell, row comparison, best of column, multi-hop (a table plus the sentence that names its dataset, or two tables) |
| G115-G120 | `numeric_table_text` | Table values that exist only as flattened body or caption text (tables PyMuPDF missed) |
| G121-G123 | `table_refusal` | Plausible numbers that are **not** in the corpus, each next to a distractor (a "1%" that means something else; a dataset used for training but never evaluated). Absence checked by searching the index |
| G124-G127 | `method` | Questions that trigger query expansion |
| G128-G133 | `unnamed_target` | Paraphrases without the method name |

Table questions in v2: 29 (6 from v1, 23 new). Every quote passes
`python -m eval.validate_golden --dataset eval/golden_v2.json` against the real index.

## Owner spot-check (at least 10)

For each item, run the command and confirm that the question is fair, the reference answer is
right, and the quoted chunk really says it. Then set `provenance.reviewed_by_owner` to `true` in
`eval/golden_v2.json`, or note the problem here.

| # | Item | Command |
|---|---|---|
| 1 | G59 (two-table fix) | `python -m eval.review_golden G59 --dataset eval/golden_v2.json --grep "BSDS500"` |
| 2 | G26 (label fix) | `python -m eval.review_golden G26 --dataset eval/golden_v2.json --grep "subsequent assignments"` |
| 3 | G03 (label fix) | `python -m eval.review_golden G03 --dataset eval/golden_v2.json --grep "expanding path"` |
| 4 | G01 (second source) | `python -m eval.review_golden G01 --dataset eval/golden_v2.json` |
| 5 | G103 (BSDS500 tie) | `python -m eval.review_golden G103 --dataset eval/golden_v2.json` |
| 6 | G108 (UCMD comparison) | `python -m eval.review_golden G108 --dataset eval/golden_v2.json --grep "SVM"` |
| 7 | G110 (multi-hop, Table X) | `python -m eval.review_golden G110 --dataset eval/golden_v2.json --grep "linear evaluation"` |
| 8 | G112 (cars, CRF) | `python -m eval.review_golden G112 --dataset eval/golden_v2.json --grep "Overall Accuracy"` |
| 9 | G116 (DEC, caption text) | `python -m eval.review_golden G116 --dataset eval/golden_v2.json --grep "w/o backprop"` |
| 10 | G120 (IIC Potsdam) | `python -m eval.review_golden G120 --dataset eval/golden_v2.json --grep "Potsdam-3"` |
| 11 | G121 (refusal trap) | `python -m eval.review_golden G105 --dataset eval/golden_v2.json --grep "surpassed the existing results"` (G105 is from the same paper; the search tool ignores punctuation, so search a phrase, not "1%") |
| 12 | G130 (unnamed SwAV) | `python -m eval.review_golden G130 --dataset eval/golden_v2.json --grep "swapped"` |

## Owner spot-check log

| Date | Item | Checked | Verdict |
|---|---|---|---|
| 2026-11-19 | G110 | PDF page 5 viewed by the owner: the table with UCMD 100% = 80.67 has the caption "TABLE X: Results for ResNet50 linear evaluation with Imagenet weights" directly below it; 99.35 appears in the same-dataset results | ok |
| 2026-11-19 | G59, G26, G03, G01, G103, G108, G112, G116, G120, G121, G130 | Commands run by the owner; assistant's reading of each output given in chat; awaiting the owner's verdict | pending |

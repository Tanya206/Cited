# Walkthrough: 5B, evaluation (part 1: golden v1 and the retrieval ladder)

Branch `ws/5b-eval`. Part 1 made no LLM calls. Results:
`eval/results/ladder_golden_v1_2026-11-19.md` (summary) and `.json` (every item).

## 1. Golden v1 is frozen

The 2026-11-12 baseline was measured on `eval/golden_dataset.json` (last changed 2026-11-07).
That content is now `eval/golden_v1.json` and is never edited. A test pins a hash of the parsed
JSON:

```powershell
.\venv\Scripts\python.exe -m pytest -q tests/test_golden_v1_frozen.py -v
```

Why it matters: if the questions change, every number changes, and an old score compared with
a new one would be measuring two different exams. Fixes go into v2; v1 and v2 numbers are never
compared directly.

## 2. The ladder: what each component adds

Run it yourself (about 3 minutes, offline, no LLM):

```powershell
$env:TQDM_DISABLE = "1"; $env:HF_HUB_OFFLINE = "1"; .\venv\Scripts\python.exe -m eval.run_ladder
```

Five configurations on the same 60 questions, each ranking a 20-candidate pool, each scored at
k=6 (what the generator actually sees after rerank) and k=20 (the candidate pool):

| Step | page hit @6 | page hit @20 | page MRR @6 |
|---|---|---|---|
| vector only | 41/60 (0.683) | 55/60 (0.917) | 0.448 |
| BM25 only | 42/60 (0.700) | 55/60 (0.917) | 0.403 |
| hybrid RRF | 50/60 (0.833) | 56/60 (0.933) | 0.503 |
| + query expansion | 50/60 (0.833) | 56/60 (0.933) | 0.503 |
| + rerank (served) | 48/60 (0.800) | 56/60 (0.933) | 0.542 |

Read the `.md` file for doc-level numbers and every comparison.

## 3. How to read a difference honestly

With 60 questions, one question is 1.7 points, so a raw difference is not enough. Two tools:

- **Exact McNemar test on page hits.** Only questions where the two configurations disagree
  carry information. If neither configuration is better, each disagreement is a coin flip.
  Vector to hybrid at k=6: 11 questions gained, 2 lost, p=0.022.
- **Paired bootstrap for MRR.** Resample the 60 questions 10,000 times (seed 0) and look at the
  middle 95% of the mean change. If that interval contains 0, this sample can't tell the
  two configurations apart.

Caveat: 10 comparisons were run. With a Bonferroni correction (0.05/10 = 0.005), none of the
p-values below survives. Treat the hybrid result as consistent evidence, not proof.

## 4. What the ladder found

1. **Hybrid earns its place.** At k=6 it beats vector (11 gained / 2 lost, p=0.022) and BM25
   (10/2, p=0.039, and the page-MRR CI [+0.014, +0.184] excludes 0). Vector and BM25 alone are
   tied (10/9). They find different pages, which is exactly why fusing them helps.
2. **The reranker shows no measurable benefit here.** At k=6: 2 gained (G18, G42), 4 lost
   (G01, G14, G41, G48), p=0.69. Page MRR +0.039 but the CI [-0.065, +0.143] includes 0.
   It also drops the right paper out of the top 6 for 2 questions (doc hit 59 to 57). This
   is not proof that it hurts. It means this golden set gives no evidence that it helps, and
   it costs latency (to be measured in 5D). Not changed yet: a pipeline change needs a
   head-to-head on v2 with answer quality, not retrieval alone.
3. **Query expansion is effectively untested.** Its rules fire on 1 of 60 questions (G07).
   "No change" here means "not exercised", not "useless".
4. **The harness is trustworthy.** It reproduces the saved 2026-11-12 baseline item by item:
   0 mismatches across 60 items.

## 5. Interview framing

"I ran an ablation on my own pipeline. Hybrid retrieval clearly beat each retriever alone at
the k the generator sees, consistent with dense and lexical search finding different evidence.
The cross-encoder reranker, which I'd assumed was helping, showed no significant gain on my
60-question set: it fixed two questions and broke four. I didn't rip it out on that evidence,
because 60 author-written questions is a small sample, but I flagged it and planned a larger
test that includes latency and answer quality."

---

# Part 2: golden v2, v2 ladder, providers, and the evaluation runner

Branch `ws/5b-eval-2`. Still no LLM calls.

## 6. The golden review

Read `eval/GOLDEN_REVIEW.md` first. Headlines:

- **2 of the 4 baseline page misses were label errors.** G03 and G26 are also answered on page 1,
  which was not labelled. v1 slightly understated page hit. v1 stays frozen; v2 fixes the labels.
- **G59 was ambiguous.** W-Net's page 8 has two tables: 0.58 on BSDS300, 0.57 on BSDS500.
  Confirmed by reading the captions straight from the PDF:

```powershell
.\venv\Scripts\python.exe -m eval.review_golden G59 --dataset eval/golden_v2.json --grep "BSDS500"
```

- **Two-paper items were scored too leniently.** A page number from the wrong paper counted. See
  the test that pins the old behaviour:

```powershell
.\venv\Scripts\python.exe -m pytest -q tests/test_retrieval_metrics.py -v
```

v2 = 60 v1 answerable items (19 with declared fixes) + 33 new: 23 table questions (14 from
structured table chunks, 6 from table values that survive only as text, 3 that must be
refused), 4 that trigger query expansion, 6 paraphrases that do not name the method.

## 7. The ladder on v2 (n=90)

```powershell
Get-Content eval\results\ladder_golden_v2_2026-11-19.md
```

```powershell
Get-Content eval\results\ladder_subsets_golden_v2_2026-11-19.md
```

- Hybrid beats vector at k=6 by 15 gained / 2 lost (p=0.002): this one survives a Bonferroni
  correction over 10 comparisons.
- The reranker still shows no measurable benefit (3 gained / 5 lost, p=0.73).
- **Table questions: hybrid puts the right page in the top 6 for 26 of 26.** Retrieval is not
  where tables fail. If tables fail, it is in reading the right number, which needs an
  answer-level check. That changes how 5F (Docling) should be judged; see gap S9.

## 8. Providers (`docs/research/llm-providers.md`)

- Generator: stay on Groq, the only verified free option allowed behind a public demo.
  Cerebras needs a card; Gemini's free tier may not serve EEA users and lets humans review prompts.
- Judge: NVIDIA NIM, a separate budget; its terms allow evaluation, not production.

## 9. The evaluation runner

```powershell
.\venv\Scripts\python.exe -m eval.run_ragas --help
```

- Answers are collected at the served configuration (20 retrieved, 6 reranked), not 50/12.
- Every Ragas score is saved the moment it exists, one line per (item, metric), with the judge,
  generator, prompt version, dataset hash, judge calls and tokens. A quota error loses nothing.
- Setting only some of the `RAGAS_*` variables is now an error, so the judge key can never be
  sent to the generator's address.

---

# Part 3: the 5-item pilot

Read `eval/results/ragas_pilot_2026-11-19.md`. What to take from it:

1. **Measure before you spend.** The pilot replaced every estimate with a provider-reported
   number: 2,830 Groq tokens per answer (69% of the output is hidden reasoning), 10 judge calls
   and 21,504 judge tokens per item. That is what sizes the full run, not a guess.
2. **Pick a judge by evidence, not by size.** The 1-trillion-parameter model timed out. The judge
   is the model that finished every metric fast with valid JSON, and it agreed with a second
   judge. Agreement on items at 1.0 proves little; the one item below 1.0 was checked by hand.
3. **A low score is a question, not a verdict.** G09's 0.857 was a real faithfulness problem
   (the answer added "NT-Xent", which no retrieved chunk contains). G106's 0.49 answer relevancy
   was a metric artefact (a bare "88.43%" cannot regenerate the question).
4. **Pilots find bugs.** A second server on port 8000, a "60ms" parsed as 60 minutes, and a
   base URL without `/v1`: all three would have wasted the full run.

See the generator's own token counts for one answer:

```powershell
Get-Content eval\results\ragas_pilot_nemotron-3-ultra_2026-11-19.jsonl | Select-Object -First 4
```

# LLM providers: verified facts

Rule 11: every limit and term here is cited with the page and the date it was read. Community
reports are labelled as such. Nothing here is from memory.

## NVIDIA NIM (API Catalog, build.nvidia.com): candidate for the Ragas judge

Read 2026-11-18.

| Item | Finding | Source |
|---|---|---|
| Endpoint | OpenAI-compatible, base `https://integrate.api.nvidia.com`, path `/v1/chat/completions` | [NVIDIA LLM API reference](https://docs.api.nvidia.com/nim/reference/llm-apis) |
| Purpose allowed | Trial access "for limited trial purposes only and without use of the API Service or Generated Content in production" (s1.2); without a paid subscription, "internal testing and evaluation purposes, not in production" (s1.4) | [NVIDIA API Trial Terms of Service](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf) (PDF metadata dated 2025-10-07) |
| Data use | NVIDIA collects "User Content and Generated Content to improve NVIDIA products and services, including AI models" (s3.3(iv)); use is logged for security and abuse monitoring | same PDF |
| Credits | Trial credits deducted per use; the amount is not stated in the terms | same PDF, s1.4 |
| Rate limit | Not published officially. NVIDIA's FAQ: "The rate of requests will vary per model queried"; check the account page on build.nvidia.com. Community reports: about 40 requests per minute | [NVIDIA NIM FAQ](https://forums.developer.nvidia.com/t/nvidia-nim-faq/300317); community: [forum thread](https://forums.developer.nvidia.com/t/request-for-nvidia-nim-api-rate-limit-increase-40-200-rpm/375340), [third-party summary](https://news.creeta.com/en/nvidia-nim-free-tier-limits-2026/) |
| Card needed | Not mentioned in the FAQ or terms | as above |
| Production use | Needs an NVIDIA AI Enterprise licence (FAQ) | NVIDIA NIM FAQ |
| Competing use | May not use the service or outputs to build competing products (s4.12) | Trial Terms PDF |
| Models (public list) | 32 IDs from `GET https://integrate.api.nvidia.com/v1/models` (no key). Large general models: `mistralai/mistral-large-4-1t-a52b`, `moonshotai/kimi-k3.1-pro`, `nvidia/nemotron-3-ultra-550b-a55b`, `google/gemma-4-31b-it`, `z-ai/glm-5.3-flash` | API call, 2026-11-18 |

**Consequences for this project**

- Judge role: offline Ragas scoring is internal evaluation, which the terms allow.
- Generator role on the public AWS demo: that is production use, which the trial terms forbid.
  NIM is therefore **not** a candidate for the deployed generator.
- Data: the judge receives questions, answers and excerpts of the papers. No personal data is
  sent. NVIDIA may use this content to improve its products; acceptable for paper excerpts,
  noted here.
- Owner's account page (read by the owner, 2026-11-18): **API rate limit 40 requests per
  minute**. This matches the community reports. Credit balance and any daily cap: not shown on
  the page. They will be measured in the 5-item pilot instead: count the calls, record every
  HTTP status, and stop on the first 402/429 that is not a per-minute limit.
- Planning consequence: Ragas makes several judge calls per item, so 40 RPM is a speed limit
  rather than a hard blocker. The real calls per item are measured in the pilot before any
  run is sized.
- Judge model: picked by a head-to-head on the 5-item pilot (5B), not chosen from a name.

## Generator survey (read 2026-11-19)

The generator sits behind the public demo, so its free terms must allow serving other people,
with no card.

| Provider | Free limit (verified) | Card | Data use on free tier | Behind a public demo? | Source |
|---|---|---|---|---|---|
| **Groq** (incumbent, `openai/gpt-oss-20b`) | Page shows *Developer-plan* limits only: 30 RPM, 1K requests/day, 8K TPM, 200K TPD for gpt-oss-20b. Free-plan numbers are in the account's limits page. Limits are per organization **and** per model | No | "By default, Groq does not retain customer data for inference requests"; logs for troubleshooting or abuse up to 30 days; Zero Data Retention can be enabled. Training use: not stated | Nothing found that forbids it | [Groq rate limits](https://console.groq.com/docs/rate-limits), [Groq "Your data"](https://console.groq.com/docs/your-data) |
| Cerebras | gpt-oss-120b 5 RPM, 1M TPD (Free Trial) | **Yes**: "$5 in free credits after adding a verified payment method"; API inactive without one | n/a | Excluded by rule 11 | [Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits) |
| Google Gemini API | Text-model free limits not on the public page (linked to the AI Studio account page) | Not stated | "Google uses the content you submit ... to provide, improve, and develop Google products"; "human reviewers may read, annotate, and process your API input and output" | **No**: "You may use only Paid Services when making API Clients available to users in the European Economic Area"; a public demo is reachable from the EEA | [Gemini API terms](https://aistudio.google.com/docs/terms) (effective 2026-03-23), [rate limits](https://aistudio.google.com/docs/rate-limits) |
| NVIDIA NIM | 40 RPM (owner's account) | Not mentioned | Used to improve NVIDIA products | **No**: trial is evaluation-only, not production | see above |
| Local Ollama (owner's laptop) | Hardware-bound; no quota | No | Stays on the laptop | Not for the AWS demo (no GPU there) | Ollama 0.21.2 installed; models `mistral` (7B), `phi3`, `mxbai-embed-large`, all about 2 years old |

**Recommendation**

- **Generator: stay on Groq.** It is the only verified free option allowed behind a public demo.
  Its retention policy is good. Its real constraint is the daily token budget.
  **Owner's Groq limits page (read by the owner, 2026-11-19), chat completions:**
  `openai/gpt-oss-20b` 30 RPM, 1K RPD, 8K TPM, 200K TPD (same for `openai/gpt-oss-120b` and
  `qwen/qwen3.8-27b`; each model has its own budget). These equal the public Developer-plan
  table.

  What that means, using the measured prompt size of the 5 pilot items (about 2,100-2,500
  prompt tokens per answer, 8.5K-10K characters; output including reasoning tokens not yet
  measured, so 3,000-4,500 tokens per answer is an estimate):
  - **Tokens per minute is the tight limit:** 8K TPM allows about 2 answers per minute.
  - **Daily:** 200K TPD is about 45-65 answers per day. The 90 answerable v2 items need about
    2 days of budget, and repair calls (which re-send the whole prompt) add to that.
  - **The public demo shares this same budget.** The request cap in 5G must leave room for it,
    or the demo and evaluation must run on different days.
- **Judge: NVIDIA NIM**, on a separate budget, so evaluation no longer competes with the demo.
- **Fallback if a free tier disappears:** local Ollama for evaluation runs (slow on CPU; the
  installed models are old and small, and small models are often weak judges, so a judge
  fallback needs its own head-to-head before any number is reported). For the demo, the
  fallback is a smaller Groq model with its own per-model budget, which changes answers and
  needs a re-collection.

**Budget arithmetic for the generator** (to be replaced by measured tokens from the pilot):
the served configuration sends 6 reranked chunks of up to 400 embedding tokens each, so an
answer prompt is a few thousand tokens. At the Developer-plan 200K TPD, collecting answers for
all 90 v2 answerable items could need more than one day. The pilot measures the real number.

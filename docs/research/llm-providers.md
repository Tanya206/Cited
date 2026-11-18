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

## Generator: second free provider

To be surveyed in 5B task 2 (must allow use behind a public demo).

# Cited Backend Study Notes

## 1. The Backend Mental Model

Cited is a FastAPI service that answers research questions using evidence from an indexed PDF corpus.

```text
HTTP request
  -> validate input
  -> retrieve evidence
  -> rerank evidence
  -> ask the language model to answer from evidence
  -> build citations
  -> record observability data
  -> return a typed JSON response
```

The backend is the part of the application that receives requests, runs the application rules, talks to retrieval and model services, and returns a response. The browser or Streamlit UI is a client of this backend.

## 2. File Responsibilities

| File | Responsibility | Called or imported by |
| --- | --- | --- |
| `app/main.py` | Creates the FastAPI app and initializes shared services at startup | Uvicorn |
| `app/models/schemas.py` | Defines validated request and response contracts | `app/api/routes.py` |
| `app/core/query_validation.py` | Deterministically rejects incomplete questions | `app/api/routes.py` |
| `app/api/routes.py` | Coordinates the complete answer request and serves papers/evidence | FastAPI |

## 3. `app/main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    app.state.services = load_services()
    yield
```

### What this does

- `FastAPI(...)` creates the web application.
- `lifespan` runs startup and shutdown logic around the application lifetime.
- `load_dotenv()` loads local environment variables such as API keys.
- `load_services()` loads Chroma, BM25, the embedding model, and the reranker once.
- `app.state.services` stores those shared objects for request handlers.
- `yield` means the application is now running.

### Why load models once?

Embedding and reranking models are expensive to load. Loading them for every request would cause high latency and waste memory. Startup loading gives each request access to already-initialized services.

### Important production concern

Startup can fail if indexes, models, or environment configuration are missing. That is preferable to silently serving incorrect answers, but health checks should make the failure visible.

## 4. `app/models/schemas.py`

Pydantic models are API contracts.

### `AnswerRequest`

```python
class AnswerRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1_000)
    retrieve_k: int = Field(default=20, ge=5, le=50)
    rerank_k: int = Field(default=6, ge=1, le=12)
```

This protects the service from invalid input and unbounded resource usage.

- `query` must be between 3 and 1,000 characters.
- `retrieve_k` controls how many candidates retrieval returns.
- `rerank_k` controls how many candidates are reranked.
- Lower and upper bounds protect latency and context size.

### `Citation`

A citation connects generated output to its source evidence:

- `chunk_id`: the exact indexed chunk.
- `doc_id`: the paper identifier.
- `page_number`: the source page.
- `paper_path`: the original PDF page link.
- `highlight_path`: the rendered evidence image link.

### `AnswerResponse`

The response includes the answer, citations, refusal state, and retrieval diagnostics. The diagnostic IDs are useful for debugging and evaluation without exposing internal model objects.

## 5. `app/core/query_validation.py`

This is a deterministic guard, not an LLM call.

```python
normalized = " ".join(query.lower().split())
```

Normalization makes whitespace and capitalization irrelevant.

The validator accepts a query when:

1. It has at least three words.
2. It ends with a question mark or starts with an allowed research/search phrase.

Examples:

- Accepted: `What is MS-SSIM?`
- Accepted: `Find the paper written by Tanya Sharma`
- Rejected: `MS-SSIM`
- Rejected: an empty string

This prevents expensive retrieval and generation for bare keywords. It also reduces the chance that the system produces an answer to a request the user did not actually ask.

## 6. `app/api/routes.py`

`routes.py` is the orchestration layer. It coordinates specialized services rather than implementing every algorithm itself.

### `Services`

The dataclass groups shared dependencies:

- Chroma collection.
- Embedding model.
- BM25 retriever.
- Chunk metadata map.
- Cross-encoder reranker.

This makes dependencies explicit and gives request handlers one application-state object to use.

### `load_services()`

This function opens the persistent vector database, loads BM25, loads the embedding model, and constructs the reranker. It runs during application startup from `main.py`.

### `GET /health`

Returns a small health response including the current chunk count. It is useful for checking that the API process is alive and that the index is accessible.

### `GET /papers/{doc_id}`

Serves a PDF from `data/raw_papers`. `paper_path()` resolves the path and verifies that it stays inside the approved corpus directory. This prevents a user-controlled document ID from becoming a path traversal vulnerability.

### `GET /evidence/{chunk_id}/highlight`

Finds the chunk metadata, opens the corresponding PDF page, searches for query phrases, adds pale turquoise highlight annotations, and returns a PNG image.

Highlighting is approximate because PDF text extraction and coordinates can be imperfect. Retrieval correctness and highlight precision are separate concerns.

### `POST /answer`

The complete request lifecycle is:

1. FastAPI validates the JSON body using `AnswerRequest`.
2. `is_actionable_question()` rejects incomplete requests.
3. `answer_trace()` starts a Langfuse observation.
4. `hybrid_retrieve()` performs vector and BM25 retrieval.
5. The trace records the retrieved count.
6. `services.reranker.rerank()` reorders candidates.
7. The trace records the reranked count and chunk IDs.
8. `generate_cited_answer()` asks Groq for an evidence-grounded answer.
9. Returned citation IDs are mapped back to chunk metadata.
10. `AnswerResponse` is constructed and validated.
11. The trace records output data.
12. The trace closes and is flushed.

### Error behavior

- Invalid request shape: FastAPI returns a validation error.
- Incomplete question: the endpoint returns a controlled refusal.
- Missing paper or evidence chunk: the relevant endpoint returns `404`.
- LLM/provider failure: the route converts `GenerationError` to `502 Bad Gateway`.

`502` is appropriate because the API is alive but an upstream provider failed. Raw stack traces and API keys are not returned to users.

## 7. Backend Design Decisions

### Why FastAPI?

- Type-safe request and response validation through Pydantic.
- Clear route definitions.
- Good support for asynchronous and service-oriented Python applications.
- Automatic API documentation.

### Why keep retrieval outside the route?

The route should orchestrate. Retrieval is a separate domain component that can be tested, benchmarked, and changed independently.

### Why use explicit response models?

They prevent accidental response-shape changes and give frontend developers a stable contract.

### Why use bounded request parameters?

Search depth affects CPU, memory, latency, and LLM token usage. Bounds protect the service from accidental or abusive values.

### Why use application state?

Models and indexes are shared read-heavy resources. Application state avoids reloading them for every request.

## 8. Questions You Should Be Able To Answer

### Request lifecycle

**What happens after the user presses Search?**

Streamlit sends JSON to `POST /answer`. FastAPI validates it, the route validates the question, retrieval finds candidates, reranking selects the best evidence, Groq generates a grounded answer, citations are built, Langfuse records the operation, and JSON is returned.

**Where is the answer generated?**

In `app/core/generation.py`, called by the `/answer` route.

**Where does the route get its models?**

From `request.app.state.services`, initialized during the FastAPI lifespan.

**Why does the route return 502 instead of 500 for Groq failure?**

The API itself is functioning; an upstream answer provider failed. `502` communicates that distinction to clients and operators.

**What prevents path traversal?**

`paper_path()` resolves the candidate path and verifies that its parent is exactly `data/raw_papers`.

**What happens if Langfuse is unavailable?**

Observability should be best-effort. A tracing failure must not replace a valid answer with an application failure.

## 9. Backend Failure-Debugging Checklist

1. Check `GET /health`.
2. Check the Uvicorn startup log for model/index loading failures.
3. Check request validation errors.
4. Check retrieval and reranking counts in the response.
5. Check the provider error detail for `502` responses.
6. Check Langfuse for latency and failure metadata.
7. Reproduce the same request with PowerShell or a test.
8. Inspect the relevant layer instead of changing the whole system.

## 10. Backend Summary

The backend is a typed orchestration service. `main.py` starts the application and initializes expensive dependencies. `schemas.py` defines the API contract. `query_validation.py` rejects unusable questions. `routes.py` coordinates retrieval, reranking, generation, citations, error handling, and tracing. The specialized AI components remain separate so they can be tested and improved independently.

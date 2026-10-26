# Cited

Cited is a research-paper RAG application for a 44-paper computer-vision corpus.
It extracts page-level elements from PDFs, indexes body text, captions, and
reliable tables, combines vector and BM25 retrieval with Reciprocal Rank
Fusion, reranks locally, and returns answers whose citations are checked
against retrieved evidence.

## Run Locally

```powershell
cd C:\Users\tanya\Desktop\Cited
.\venv\Scripts\Activate.ps1
pip install streamlit pytest

# Rebuild artifacts after adding or changing PDFs.
python app\ingestion\extract.py
python app\core\chunking.py
python app\core\embeddings.py
python app\core\bm25_index.py

# Inspect retrieval before involving an LLM.
python -m scripts.debug_retrieval "How does SimCLR use augmentations?"

# Add GROQ_API_KEY=... to .env. GROQ_MODEL is optional; it defaults to
# openai/gpt-oss-20b. Then start the API and UI in separate terminals.
uvicorn app.main:app --reload
streamlit run frontend\streamlit_app.py
```

Open `http://127.0.0.1:8501` for the UI and `http://127.0.0.1:8000/docs` for
the API documentation.

## Verify

```powershell
python -m pytest -q
```

The test suite covers deterministic fusion and generation-response validation;
manual retrieval checks remain important because relevance is corpus-specific.

## Golden Dataset Review

The dataset is intentionally blocked from strict regression use until each
answerable item has a manually verified source quote. Review candidates from
the project root, then add stable `doc_id`, `page_number`, and `quote` evidence
to the item (do not use positional chunk IDs):

```powershell
python -m eval.review_golden G10 --grep "momentum update"
python -m eval.validate_golden
python -m eval.validate_golden --strict
```

For the complete evaluation workflow, including retrieval baselines, Ragas,
Langfuse, CI, and the decision log, see [docs/EVALUATION.md](docs/EVALUATION.md).

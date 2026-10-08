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

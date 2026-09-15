"""
Embedding and vector storage for Cited.

Embeds all chunks with bge-small-en-v1.5 as plain passages (no
instruction prefix — that's applied only to queries, at retrieval time
in Phase 2) and stores them in a persistent Chroma collection with full
metadata intact for citation traceability.
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "cited_chunks"
BATCH_SIZE = 64


def load_chunks(path: str) -> list[dict]:
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def flatten_metadata(chunk: dict) -> dict:
    """Chroma metadata values must be str/int/float/bool — drop the
    chunk text and id (stored separately) and coerce anything else to
    a safe type, keeping every field that supports citation."""
    metadata = {}
    for key, value in chunk.items():
        if key in ("chunk_id", "text"):
            continue
        if value is None:
            continue
        metadata[key] = value if isinstance(value, (str, int, float, bool)) else str(value)
    return metadata


def embed_and_store(chunks_path: str, chroma_path: str, collection_name: str) -> None:
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    chunks = load_chunks(chunks_path)
    print(f"Loaded {len(chunks)} chunks")

    client = chromadb.PersistentClient(path=chroma_path)

    try:
        client.delete_collection(name=collection_name)  # start clean every run — Chroma
        # silently skips duplicate-ID inserts rather than raising, so a stale
        # collection can quietly drift out of sync with chunks.jsonl after any
        # re-run (e.g. changed chunk IDs from a chunking fix). Resetting is cheap
        # here (2,696 short chunks) so there's no reason to risk staleness.
    except Exception:
        pass  # collection doesn't exist yet on the first-ever run — fine

    collection = client.get_or_create_collection(name=collection_name)

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["text"] for c in batch]

        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        collection.add(
            ids=[c["chunk_id"] for c in batch],
            embeddings=embeddings,
            documents=texts,
            metadatas=[flatten_metadata(c) for c in batch],
        )
        print(f"  embedded {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    assert collection.count() == len(chunks), \
        f"count mismatch: Chroma has {collection.count()}, expected {len(chunks)}"
    print(f"\nStored {collection.count()} chunks in Chroma collection '{collection_name}'")


def sanity_check(chroma_path: str, collection_name: str) -> None:
    """Run a couple of manual test queries and print what comes back —
    eyeball relevance before trusting this as Phase 2's foundation."""
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection(name=collection_name)
    model = SentenceTransformer(MODEL_NAME)

        # NOTE: queries here are embedded plain, with no instruction prefix —
    # correct for now since the query/passage asymmetry doesn't exist until
    # Phase 2. This previews symmetric similarity only; re-validate once
    # the prefix is added, since that changes what "relevant" means for queries.

    test_queries = [
        "contrastive learning loss function",
        "mIoU results on Potsdam dataset",
    ]

    for query in test_queries:
        query_embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=3)

        print(f"\nQuery: \"{query}\"")
        for doc_id, chunk_type, page, text in zip(
            [m["doc_id"] for m in results["metadatas"][0]],
            [m["chunk_type"] for m in results["metadatas"][0]],
            [m["page_number"] for m in results["metadatas"][0]],
            results["documents"][0],
        ):
            print(f"  [{chunk_type}] {doc_id[:40]} p.{page}: {text[:100]}...")


if __name__ == "__main__":
    embed_and_store("data/chunks.jsonl", CHROMA_PATH, COLLECTION_NAME)
    print("\n--- Sanity check ---")
    sanity_check(CHROMA_PATH, COLLECTION_NAME)
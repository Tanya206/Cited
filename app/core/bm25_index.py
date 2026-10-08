"""
BM25 keyword index for Cited.

Built once over chunks.jsonl, alongside the Chroma vector store — this
is the exact-term half of hybrid retrieval, catching cases like
"Potsdam-3" or "STEGO" that pure embedding similarity can miss.
"""

import json
import os
import bm25s
import Stemmer

STEMMER = Stemmer.Stemmer("english")
CHUNKS_PATH = "data/chunks.jsonl"
INDEX_DIR = "data/bm25_index"


def load_chunks(path: str) -> list[dict]:
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def build_index(chunks_path: str, index_dir: str) -> None:
    chunks = load_chunks(chunks_path)
    print(f"Loaded {len(chunks)} chunks")

    texts = [c["text"] for c in chunks]
    chunk_ids = [c["chunk_id"] for c in chunks]

    corpus_tokens = bm25s.tokenize(texts, stopwords="en", stemmer=STEMMER)
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    os.makedirs(index_dir, exist_ok=True)
    retriever.save(index_dir)

    # bm25s retrieves by corpus position, not chunk_id. Persist the complete
    # chunk record so a BM25 hit carries the same citation metadata as a
    # vector hit (including a table's source crop when present).
    id_map_path = os.path.join(index_dir, "chunk_id_map.json")
    with open(id_map_path, "w", encoding="utf-8") as f:
        json.dump(
            chunks,
            f,
        )

    print(f"BM25 index built and saved to {index_dir}")
    print(f"Chunk ID mapping saved to {id_map_path}")


def load_index(index_dir: str) -> tuple:
    retriever = bm25s.BM25.load(index_dir)
    id_map_path = os.path.join(index_dir, "chunk_id_map.json")
    with open(id_map_path, "r", encoding="utf-8") as f:
        chunk_id_map = json.load(f)
    return retriever, chunk_id_map


def bm25_search(retriever, chunk_id_map: list[dict], query: str, k: int = 10) -> list[dict]:
    """Return top-k chunks by BM25 score, with citation metadata attached."""
    query_tokens = bm25s.tokenize([query], stopwords="en", stemmer=STEMMER)
    positions, scores = retriever.retrieve(query_tokens, k=k)

    results = []
    for rank, (pos, score) in enumerate(zip(positions[0], scores[0]), start=1):
        chunk = chunk_id_map[pos]
        results.append({**chunk, "rank": rank, "bm25_score": float(score)})
    return results


def sanity_check(index_dir: str) -> None:
    """Same two test queries used for the vector-search sanity check —
    lets you directly compare what BM25 surfaces vs. what embedding
    similarity surfaced in Phase 1."""
    retriever, chunk_id_map = load_index(index_dir)

    test_queries = [
        "contrastive learning loss function",
        "mIoU results on Potsdam dataset",
    ]

    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        results = bm25_search(retriever, chunk_id_map, query, k=5)
        for r in results:
            print(f"  {r['rank']}. [{r['chunk_type']}] {r['doc_id'][:40]} p.{r['page_number']} "
                  f"(score={r['bm25_score']:.2f}): {r['text'][:80]}...")


if __name__ == "__main__":
    build_index(CHUNKS_PATH, INDEX_DIR)
    print("\n--- Sanity check ---")
    sanity_check(INDEX_DIR)

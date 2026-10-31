"""
Hybrid retrieval for Cited: BM25 + vector search, combined via
Reciprocal Rank Fusion. Written by hand rather than using a library's
built-in hybrid mode, so the fusion logic is fully explainable.
"""

import re

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.bm25_index import load_index, bm25_search

MODEL_NAME = "BAAI/bge-small-en-v1.5"
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "cited_chunks"
BM25_INDEX_DIR = "data/bm25_index"

# BGE models expect this instruction prefix on queries only — passages
# were embedded plain. This asymmetry is why query and passage
# embedding logic live in different places (Phase 1 vs. here).
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def expand_query(query: str) -> str:
    """Add transparent lexical cues for procedural and algorithm questions."""
    normalized = query.lower()
    additions: list[str] = []
    if re.search(r"\b(stage|stages|step|steps|process|procedure)\b", normalized):
        additions.extend(["algorithm steps", "procedure", "method", "first", "then"])
    if "spectral clustering" in normalized:
        additions.extend(["graph", "affinity matrix", "eigenvectors", "laplacian", "k-means"])
    return f"{query} {' '.join(dict.fromkeys(additions))}" if additions else query

def embed_query(text: str, model: SentenceTransformer):
    prefixed = QUERY_INSTRUCTION + text
    return model.encode([prefixed], normalize_embeddings=True).tolist()


def vector_search(collection, model: SentenceTransformer, query: str, k: int = 20) -> list[dict]:
    query_embedding = embed_query(query, model)
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    output = []
    for rank, (cid, meta, doc, dist) in enumerate(zip(
        results["ids"][0], results["metadatas"][0], results["documents"][0], results["distances"][0]
    ), start=1):
        output.append({
            **meta,
            "chunk_id": cid,
            "text": doc,
            "rank": rank,
            "vector_distance": float(dist),
        })
    return output


def reciprocal_rank_fusion(result_lists: list[list[dict]], k: int = 10) -> list[dict]:
    scores: dict[str, float] = {}
    chunk_data: dict[str, dict] = {}
    ranks: dict[str, dict] = {}

    for label, results in zip(["vector", "bm25"], result_lists):
        for item in results:
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + item["rank"])
            ranks.setdefault(cid, {})[label] = item["rank"]

            if cid not in chunk_data:
                chunk_data[cid] = {
                    key: value
                    for key, value in item.items()
                    if key not in {"rank", "vector_distance", "bm25_score"}
                }
            if "vector_distance" in item:
                chunk_data[cid]["vector_distance"] = item["vector_distance"]
            if "bm25_score" in item:
                chunk_data[cid]["bm25_score"] = item["bm25_score"]

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {**chunk_data[cid], "rrf_score": round(score, 5), "ranks": ranks[cid], "found_by": list(ranks[cid].keys())}
        for cid, score in fused
    ]


def hybrid_retrieve(
    query: str,
    collection,
    embed_model: SentenceTransformer,
    bm25_retriever,
    chunk_id_map: list[dict],
    k_per_retriever: int = 20,
    k_final: int = 10,
    rrf_k: int = 10,
) -> list[dict]:
    search_query = expand_query(query)
    vector_results = vector_search(collection, embed_model, search_query, k=k_per_retriever)
    bm25_results = bm25_search(bm25_retriever, chunk_id_map, search_query, k=k_per_retriever)
    fused = reciprocal_rank_fusion([vector_results, bm25_results], k=rrf_k)
    return fused[:k_final]


def sanity_check() -> None:
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    embed_model = SentenceTransformer(MODEL_NAME)
    bm25_retriever, chunk_id_map = load_index(BM25_INDEX_DIR)

    test_queries = [
        "contrastive learning loss function",
        "mIoU results on Potsdam dataset",
    ]

    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        results = hybrid_retrieve(query, collection, embed_model, bm25_retriever, chunk_id_map, k_final=5)
        for i, r in enumerate(results, start=1):
            print(f"  {i}. [{r['chunk_type']}] {r['doc_id'][:40]} p.{r['page_number']} "
                  f"(rrf={r['rrf_score']}, ranks={r['ranks']}): {r['text'][:80]}...")


if __name__ == "__main__":
    sanity_check()

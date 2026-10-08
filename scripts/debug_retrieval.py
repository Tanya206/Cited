"""Print the production hybrid-retrieval results for one query."""

import sys

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.bm25_index import load_index
from app.core.retrieval import (
    BM25_INDEX_DIR,
    CHROMA_PATH,
    COLLECTION_NAME,
    MODEL_NAME,
    hybrid_retrieve,
)


def main() -> None:
    query = " ".join(sys.argv[1:]) or "mIoU results on Potsdam dataset"
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    model = SentenceTransformer(MODEL_NAME)
    bm25_retriever, chunk_id_map = load_index(BM25_INDEX_DIR)

    for rank, result in enumerate(
        hybrid_retrieve(query, collection, model, bm25_retriever, chunk_id_map),
        start=1,
    ):
        print(
            f"{rank}. [{result['chunk_type']}] {result['doc_id']} "
            f"p.{result['page_number']} {result['ranks']}: "
            f"{result['text'][:160]}..."
        )


if __name__ == "__main__":
    main()

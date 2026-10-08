"""HTTP route for the complete retrieve, rerank, and cited-answer flow."""

from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import quote

import chromadb
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, Response
import pymupdf
from sentence_transformers import SentenceTransformer

from app.core.bm25_index import load_index
from app.core.generation import GenerationError, generate_cited_answer
from app.core.query_validation import is_actionable_question
from app.core.reranker import Reranker
from app.core.retrieval import (
    BM25_INDEX_DIR,
    CHROMA_PATH,
    COLLECTION_NAME,
    MODEL_NAME,
    hybrid_retrieve,
)
from app.models.schemas import AnswerRequest, AnswerResponse, Citation

router = APIRouter(tags=["answers"])
RAW_PAPERS_DIR = Path("data/raw_papers").resolve()


@dataclass
class Services:
    collection: object
    embed_model: SentenceTransformer
    bm25_retriever: object
    chunk_id_map: list[dict]
    reranker: Reranker


def load_services() -> Services:
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    bm25_retriever, chunk_id_map = load_index(BM25_INDEX_DIR)
    return Services(
        collection=client.get_collection(name=COLLECTION_NAME),
        embed_model=SentenceTransformer(MODEL_NAME),
        bm25_retriever=bm25_retriever,
        chunk_id_map=chunk_id_map,
        reranker=Reranker(),
    )


def paper_path(doc_id: str) -> Path:
    """Resolve a corpus PDF without allowing paths outside raw_papers."""
    path = (RAW_PAPERS_DIR / f"{doc_id}.pdf").resolve()
    if path.parent != RAW_PAPERS_DIR or not path.is_file():
        raise HTTPException(status_code=404, detail="Paper not found.")
    return path


def highlight_rectangles(page: pymupdf.Page, text: str) -> list[pymupdf.Rect]:
    """Find several readable excerpts from a chunk on its original PDF page."""
    normalized = re.sub(r"\s+", " ", text).replace("ﬁ", "fi").replace("ﬂ", "fl")
    sentences = re.findall(r"[^.!?]{35,220}[.!?]", normalized)
    rectangles: list[pymupdf.Rect] = []

    for sentence in sorted(sentences, key=len, reverse=True):
        matches = page.search_for(sentence)
        if matches:
            rectangles.extend(matches)
        if len(rectangles) >= 8:
            break

    # Tables and malformed PDF text may not contain complete sentences.
    if not rectangles:
        for phrase in re.findall(r"[A-Za-z][A-Za-z0-9 ,;:()\-]{30,110}", normalized):
            matches = page.search_for(phrase)
            if matches:
                rectangles.extend(matches)
            if len(rectangles) >= 8:
                break
    return rectangles[:8]


@router.get("/health")
def health(request: Request) -> dict[str, str]:
    return {"status": "ok", "chunks": str(request.app.state.services.collection.count())}


@router.get("/papers/{doc_id}")
def open_paper(doc_id: str) -> FileResponse:
    """Serve a corpus PDF; browser PDF viewers use #page=N anchors."""
    return FileResponse(paper_path(doc_id), media_type="application/pdf")


@router.get("/evidence/{chunk_id}/highlight")
def highlight_evidence(chunk_id: str, request: Request) -> Response:
    """Render a cited page and mark excerpts that match the evidence chunk."""
    services: Services = request.app.state.services
    chunk = next(
        (item for item in services.chunk_id_map if item["chunk_id"] == chunk_id),
        None,
    )
    if chunk is None:
        raise HTTPException(status_code=404, detail="Evidence chunk not found.")

    with pymupdf.open(paper_path(chunk["doc_id"])) as document:
        page = document[chunk["page_number"] - 1]
        for rectangle in highlight_rectangles(page, chunk["text"]):
            annotation = page.add_highlight_annot(rectangle)
            # paleturquoise (#AFEEEE), translucent like a physical highlighter.
            annotation.set_colors(stroke=(175 / 255, 238 / 255, 238 / 255))
            annotation.set_opacity(0.55)
            annotation.update()
        pixmap = page.get_pixmap(dpi=140, alpha=False)
        return Response(content=pixmap.tobytes("png"), media_type="image/png")


@router.post("/answer", response_model=AnswerResponse)
def answer(payload: AnswerRequest, request: Request) -> AnswerResponse:
    if not is_actionable_question(payload.query):
        return AnswerResponse(
            answer=(
                "Please ask a complete research question so I can retrieve "
                "the right evidence. For example: 'What is image segmentation?'"
            ),
            citations=[],
            retrieved_count=0,
            reranked_count=0,
            refused=True,
        )

    services: Services = request.app.state.services
    retrieved = hybrid_retrieve(
        payload.query,
        services.collection,
        services.embed_model,
        services.bm25_retriever,
        services.chunk_id_map,
        k_per_retriever=payload.retrieve_k,
        k_final=payload.retrieve_k,
    )
    reranked = services.reranker.rerank(payload.query, retrieved, payload.rerank_k)

    try:
        answer_text, citation_ids, refused = generate_cited_answer(payload.query, reranked)
    except GenerationError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    by_id = {chunk["chunk_id"]: chunk for chunk in reranked}
    citations = [
        Citation(
            chunk_id=chunk_id,
            doc_id=by_id[chunk_id]["doc_id"],
            page_number=int(by_id[chunk_id]["page_number"]),
            chunk_type=by_id[chunk_id]["chunk_type"],
            source_image_path=by_id[chunk_id].get("source_image_path"),
            paper_path=f"/papers/{quote(by_id[chunk_id]['doc_id'], safe='')}#page={by_id[chunk_id]['page_number']}",
            highlight_path=f"/evidence/{quote(chunk_id, safe='')}/highlight",
        )
        for chunk_id in citation_ids
    ]
    return AnswerResponse(
        answer=answer_text,
        citations=citations,
        retrieved_count=len(retrieved),
        reranked_count=len(reranked),
        refused=refused,
    )

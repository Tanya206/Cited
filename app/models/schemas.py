"""Pydantic contracts for the public cited-answer API."""

from pydantic import BaseModel, Field


class AnswerRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1_000)
    retrieve_k: int = Field(default=20, ge=5, le=50)
    rerank_k: int = Field(default=6, ge=1, le=12)


class Citation(BaseModel):
    chunk_id: str
    doc_id: str
    page_number: int
    chunk_type: str
    source_image_path: str | None = None
    paper_path: str
    highlight_path: str


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved_count: int
    reranked_count: int
    refused: bool = False

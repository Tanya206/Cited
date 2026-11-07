"""Pydantic contracts for the public cited-answer API."""

from pydantic import BaseModel, Field
#Pydantic ensures that the data entering your Python application follows the structure and data types you expect.

class AnswerRequest(BaseModel): #This protects the service from invalid input and unbounded resource usage.
    query: str = Field(min_length=3, max_length=1_000) #Ensures the query is between 3 and 1,000 characters.
    retrieve_k: int = Field(default=20, ge=5, le=50)#controls how many candidates retrieval returns.
    rerank_k: int = Field(default=6, ge=1, le=12)#controls how many candidates reranker returns.


class Citation(BaseModel): #This ensures that each citation follows a consistent structure and data type. It connects generated output to its source evidence.
    chunk_id: str
    doc_id: str
    page_number: int
    chunk_type: str
    source_image_path: str | None = None
    paper_path: str
    highlight_path: str

#The response includes the answer, citations, refusal state, and retrieval
# diagnostics. The diagnostic IDs are useful for debugging and evaluation
# without exposing internal model objects.
class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved_count: int
    reranked_count: int
    refused: bool = False
    retrieved_chunk_ids: list[str] = Field(default_factory=list)
    reranked_chunk_ids: list[str] = Field(default_factory=list)

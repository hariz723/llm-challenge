from pydantic import BaseModel
from uuid import UUID
from typing import List


class DocumentUploadResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    blob_url: str

    class Config:
        from_attributes = True


class DocumentSearchResponse(BaseModel):
    document_id: UUID
    filename: str
    blob_url: str
    text: str
    score: float


class DocumentSearchRequest(BaseModel):
    query: str


class RAGChatRequest(BaseModel):
    query: str
    top_k: int = 5


class RAGSource(BaseModel):
    document_id: UUID
    filename: str
    blob_url: str
    text: str
    score: float


class RAGChatResponse(BaseModel):
    answer: str
    sources: List[RAGSource]
    trace_id: str | None = None
    trace_url: str | None = None

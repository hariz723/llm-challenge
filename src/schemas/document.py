from pydantic import BaseModel
from uuid import UUID


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

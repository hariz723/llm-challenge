from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class DocumentUploadResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    blob_url: str

    class Config:
        from_attributes = True  # or orm_mode = True for older Pydantic versions

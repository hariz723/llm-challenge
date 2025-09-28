from sqlalchemy.ext.asyncio import AsyncSession
from ..models.models import Document
from uuid import UUID


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(
        self, filename: str, user_id: UUID, blob_url: str
    ) -> Document:
        db_doc = Document(filename=filename, user_id=user_id, blob_url=blob_url)
        self.db.add(db_doc)
        await self.db.commit()
        await self.db.refresh(db_doc)
        return db_doc

    # Add other document-related database operations here as needed
    # async def get_document_by_id(self, doc_id: str) -> Document:
    #     return await self.db.query(Document).filter(Document.doc_id == doc_id).first()

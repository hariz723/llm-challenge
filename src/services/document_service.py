import uuid
from typing import List
from fastapi import UploadFile, HTTPException
from ..models.auth import User
from ..core.logging import logger
from ..repository.document import DocumentRepository
from ..storage.azure_storage import AzureStorage  # Import AzureStorage
from ..schemas.document import DocumentUploadResponse  # Import DocumentUploadResponse


# Placeholder for text extraction (replace with actual implementation)
def extract_text_from_file(content: bytes, filename: str) -> str:
    # This is a placeholder. In a real application, you'd use libraries
    # like python-docx, pypdf, etc., based on file extension.
    # For now, it just decodes content if it's text-like.
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning(f"Could not decode {filename} as UTF-8. Returning empty string.")
        return ""


# Placeholder for text chunking (replace with actual implementation)
def chunk_text(text: str) -> List[str]:
    # Simple chunking for demonstration
    return [text[i : i + 500] for i in range(0, len(text), 500)]


# Placeholder for ChromaDB collection (replace with actual implementation)
# This would typically involve an embedding model and ChromaDB client
class MockChromaCollection:
    def add(self, documents: List[str], ids: List[str], metadatas: List[dict]):
        logger.info(f"Adding {len(documents)} documents to ChromaDB (mocked).")
        # Simulate adding to a database
        pass


def get_or_create_collection(user_id: str):
    # This would connect to ChromaDB and get/create a user-specific collection
    logger.info(f"Getting or creating ChromaDB collection for user {user_id} (mocked).")
    return MockChromaCollection()


class DocumentService:
    def __init__(
        self, document_repository: DocumentRepository, azure_storage: AzureStorage
    ):
        self.document_repository = document_repository
        self.azure_storage = azure_storage

    async def upload_document(self, file: UploadFile, current_user: User):
        try:
            # Upload file to Azure Blob Storage
            doc_id = str(uuid.uuid4())
            blob_url = await self.azure_storage.upload_file(file, doc_id)

            # Read file content for text extraction (after upload, as file.read() consumes the stream)
            # To re-read, we might need to rewind the file or get content from storage if it's a large file.
            # For simplicity, assuming file.read() can be called again or content is passed.
            # In a real scenario, you might download from blob_url or ensure file stream is reset.
            # For now, I'll assume the file object can be read again or content is available.
            # A more robust solution would be to read content once and pass it around.
            # For this example, I'll re-read the file content.
            await file.seek(0)  # Rewind the file pointer
            content = await file.read()

            text = extract_text_from_file(content, file.filename)
            if not text.strip():
                raise HTTPException(
                    status_code=400, detail="Could not extract text from file"
                )

            chunks = chunk_text(text)
            collection = get_or_create_collection(current_user.id)

            ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

            collection.add(
                documents=chunks,
                ids=ids,
                metadatas=[
                    {"filename": file.filename, "chunk_id": i, "blob_url": blob_url}
                    for i in range(len(chunks))
                ],
            )

            # Use the repository to create the document
            db_doc = await self.document_repository.create_document(
                filename=file.filename,
                user_id=current_user.id,
                doc_id=doc_id,
                blob_url=blob_url,
            )

            return DocumentUploadResponse.model_validate(db_doc)

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise HTTPException(status_code=500, detail="Error processing document")

import uuid
from typing import List
from fastapi import UploadFile, HTTPException
from ..models.auth import User
from ..core.logging import logger
from ..repository.document import DocumentRepository
from ..storage.azure_storage import AzureStorage
from ..schemas.document import DocumentSearchResponse
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import core.constants as cons


embedding_model = SentenceTransformer(cons.EMBEDDING_MODEL_NAME)


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


def get_embedding(text: str) -> List[float]:
    return embedding_model.encode(text).tolist()


class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        azure_storage: AzureStorage,
        qdrant_client: QdrantClient,
    ):
        self.document_repository = document_repository
        self.azure_storage = azure_storage
        self.qdrant_client = qdrant_client

    def _get_or_create_collection(self, collection_name: str):
        try:
            self.qdrant_client.get_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' already exists.")
        except Exception:
            logger.info(f"Collection '{collection_name}' not found. Creating it.")
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=384, distance=models.Distance.COSINE
                ),
            )

    async def upload_document(self, file: UploadFile, current_user: User):
        try:

            blob_url = await self.azure_storage.upload_file(file, str(uuid.uuid4()))

            await file.seek(0)
            content = await file.read()

            text = extract_text_from_file(content, file.filename)
            if not text.strip():
                raise HTTPException(
                    status_code=400, detail="Could not extract text from file"
                )

            chunks = chunk_text(text)
            collection_name = str(current_user.id)
            self._get_or_create_collection(collection_name)

            # Use the repository to create the document first to get its ID
            db_doc = await self.document_repository.create_document(
                filename=file.filename,
                user_id=current_user.id,
                blob_url=blob_url,
            )

            points = []
            for i, chunk in enumerate(chunks):
                point_id = str(uuid.uuid4())
                embedding = get_embedding(chunk)
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "document_id": db_doc.id,
                            "text": chunk,
                            "filename": file.filename,
                            "chunk_id": i,
                            "blob_url": blob_url,
                        },
                    )
                )

            if points:
                self.qdrant_client.upsert(
                    collection_name=collection_name,
                    points=points,
                    wait=True,
                )

            return db_doc

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise HTTPException(status_code=500, detail="Error processing document")

    async def search_documents(
        self, query: str, current_user: User
    ) -> List[DocumentSearchResponse]:
        try:
            collection_name = str(current_user.id)
            query_embedding = get_embedding(query)

            search_result = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=5,  # Return top 5 results
            )

            results = []
            for hit in search_result:
                payload = hit.payload
                results.append(
                    DocumentSearchResponse(
                        document_id=payload["document_id"],
                        filename=payload["filename"],
                        blob_url=payload["blob_url"],
                        text=payload["text"],
                        score=hit.score,
                    )
                )
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise HTTPException(status_code=500, detail="Error searching documents")

import uuid
from typing import List
from fastapi import UploadFile, HTTPException
from ..schemas.auth import AuthenticatedUser
from ..core.logging import logger
from ..repository.document import DocumentRepository
from ..storage.azure_storage import AzureStorage
from ..schemas.document import DocumentSearchResponse, RAGChatResponse, RAGSource
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import core.constants as cons
from ..core.config import settings
import requests


embedding_model = SentenceTransformer(cons.EMBEDDING_MODEL_NAME)
EMBEDDING_DIMENSION = embedding_model.get_sentence_embedding_dimension()


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
    chunk_size = 700
    overlap = 120
    if not text.strip():
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [chunk for chunk in chunks if chunk]


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
                    size=EMBEDDING_DIMENSION, distance=models.Distance.COSINE
                ),
            )

    def _search_chunks(
        self, query: str, current_user: AuthenticatedUser, top_k: int = 5
    ) -> List[DocumentSearchResponse]:
        collection_name = str(current_user.id)
        try:
            self.qdrant_client.get_collection(collection_name=collection_name)
        except Exception:
            return []

        query_embedding = get_embedding(query)
        search_result = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k,
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

    def _generate_answer_with_llm(
        self, query: str, search_results: List[DocumentSearchResponse]
    ) -> str | None:
        if not settings.LLM_API_URL or not settings.LLM_MODEL:
            return None

        context_blocks = []
        for idx, result in enumerate(search_results, start=1):
            context_blocks.append(
                f"[Source {idx}] {result.filename}\n{result.text.strip()}"
            )

        prompt = (
            "Answer the user's question using only the provided sources. "
            "If the answer is not supported by the sources, say that clearly. "
            "Cite sources inline like [Source 1].\n\n"
            f"Question: {query}\n\n"
            f"Sources:\n\n{'\n\n'.join(context_blocks)}"
        )

        headers = {"Content-Type": "application/json"}
        if settings.LLM_API_KEY:
            headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"

        response = requests.post(
            settings.LLM_API_URL,
            headers=headers,
            json={
                "model": settings.LLM_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a careful RAG assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()

    def _generate_fallback_answer(
        self, query: str, search_results: List[DocumentSearchResponse]
    ) -> str:
        if not search_results:
            return (
                "I couldn't find any relevant document context for that question yet. "
                "Upload a document first or try a more specific query."
            )

        lines = []
        for idx, result in enumerate(search_results[:3], start=1):
            excerpt = " ".join(result.text.split())
            excerpt = excerpt[:280].rstrip()
            lines.append(f"[Source {idx}] {excerpt}")

        return (
            f"Based on the retrieved document chunks, the most relevant information for "
            f"'{query}' is:\n\n" + "\n\n".join(lines)
        )

    async def upload_document(self, file: UploadFile, current_user: AuthenticatedUser):
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

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise HTTPException(status_code=500, detail="Error processing document")

    async def search_documents(
        self, query: str, current_user: AuthenticatedUser
    ) -> List[DocumentSearchResponse]:
        try:
            return self._search_chunks(query=query, current_user=current_user, top_k=5)
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise HTTPException(status_code=500, detail="Error searching documents")

    async def answer_question(
        self, query: str, current_user: AuthenticatedUser, top_k: int = 5
    ) -> RAGChatResponse:
        try:
            search_results = self._search_chunks(
                query=query, current_user=current_user, top_k=top_k
            )
            answer = self._generate_answer_with_llm(query, search_results)
            if not answer:
                answer = self._generate_fallback_answer(query, search_results)

            return RAGChatResponse(
                answer=answer,
                sources=[
                    RAGSource(
                        document_id=result.document_id,
                        filename=result.filename,
                        blob_url=result.blob_url,
                        text=result.text,
                        score=result.score,
                    )
                    for result in search_results
                ],
            )
        except requests.RequestException as exc:
            logger.warning(f"LLM generation failed, using fallback answer: {exc}")
            search_results = self._search_chunks(
                query=query, current_user=current_user, top_k=top_k
            )
            return RAGChatResponse(
                answer=self._generate_fallback_answer(query, search_results),
                sources=[
                    RAGSource(
                        document_id=result.document_id,
                        filename=result.filename,
                        blob_url=result.blob_url,
                        text=result.text,
                        score=result.score,
                    )
                    for result in search_results
                ],
            )
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise HTTPException(status_code=500, detail="Error generating answer")

import io
import uuid
from functools import lru_cache
from typing import List
import docx
import numpy as np
from pypdf import PdfReader
from huggingface_hub import InferenceClient
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


@lru_cache(maxsize=1)
def get_hf_client() -> InferenceClient | None:
    token = settings.HUGGINGFACE_TOKEN
    if token:
        return InferenceClient(api_key=token)
    return None


embedding_model = SentenceTransformer(cons.EMBEDDING_MODEL_NAME)
EMBEDDING_DIMENSION = embedding_model.get_sentence_embedding_dimension()


def extract_text_from_file(content: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    try:
        if ext == "pdf":
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(p.strip() for p in pages if p.strip())

        if ext in ("docx", "doc"):
            doc = docx.Document(io.BytesIO(content))
            elements = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = [c.text.strip() for c in row.cells if c.text.strip()]
                    if row_text:
                        elements.append(" | ".join(row_text))
            return "\n".join(elements)

        # Fallback for plain text, markdown, code, json, csv, etc.
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1", errors="ignore")

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}")
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


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    client = get_hf_client()
    if client:
        try:
            all_vectors: List[List[float]] = []
            batch_size = 32
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                emb = client.feature_extraction(batch, model=settings.HF_EMBEDDING_MODEL)
                arr = emb if hasattr(emb, "shape") else np.array(emb)
                if arr.ndim == 3:
                    arr = np.mean(arr, axis=1)
                elif arr.ndim == 1:
                    arr = arr.reshape(1, -1)
                all_vectors.extend(arr.tolist())
            return [[float(x) for x in v] for v in all_vectors]
        except Exception as e:
            logger.warning(
                f"Hugging Face batch feature extraction failed ({e}). Falling back to local SentenceTransformer."
            )

    encoded = embedding_model.encode(texts, batch_size=32, show_progress_bar=False)
    return [[float(x) for x in v] for v in encoded.tolist()]


def get_embedding(text: str) -> List[float]:
    results = get_embeddings_batch([text])
    return results[0] if results else []


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
        if hasattr(self.qdrant_client, "query_points"):
            response = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=query_embedding,
                limit=top_k,
                with_payload=True,
            )
            hits = response.points
        else:
            hits = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
            )

        results = []
        for hit in hits:
            payload = hit.payload or {}
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

        # 1. Try Hugging Face Inference if token is configured
        client = get_hf_client()
        if client:
            try:
                hf_model = settings.HF_CHAT_MODEL or "meta-llama/Llama-3.2-3B-Instruct"
                response = client.chat_completion(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an accurate and concise RAG assistant. "
                                "Answer the question strictly using the provided sources. "
                                "Cite sources like [Source 1]. If not found in sources, state that clearly."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    model=hf_model,
                    temperature=0.2,
                    max_tokens=512,
                )
                if response and response.choices:
                    content = response.choices[0].message.content
                    if content:
                        return content.strip()
            except Exception as e:
                logger.error(f"Hugging Face chat completion failed: {e}")

        # 2. Try custom LLM_API_URL if configured
        if settings.LLM_API_URL and settings.LLM_MODEL:
            try:
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
            except Exception as e:
                logger.error(f"Custom LLM API request failed: {e}")

        return None

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

            embeddings = get_embeddings_batch(chunks)
            points = []
            for i, chunk in enumerate(chunks):
                point_id = str(uuid.uuid4())
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=embeddings[i],
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

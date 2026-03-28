from fastapi import APIRouter, Depends, UploadFile, File
from ..core.dependencies import get_current_user, DocumentServiceDep
from ..schemas.auth import AuthenticatedUser
from ..schemas.document import (
    DocumentUploadResponse,
    DocumentSearchResponse,
    DocumentSearchRequest,
    RAGChatRequest,
    RAGChatResponse,
)
from typing import List


router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    document_service: DocumentServiceDep,
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Uploads a document, processes it, and stores its chunks.
    """
    db_doc = await document_service.upload_document(file, current_user)

    return DocumentUploadResponse(
        id=db_doc.id,
        user_id=db_doc.user_id,
        filename=db_doc.filename,
        blob_url=db_doc.blob_url,
    )


@router.post("/search", response_model=List[DocumentSearchResponse])
async def search_documents(
    payload: DocumentSearchRequest,
    document_service: DocumentServiceDep,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Searches for documents similar to the query.
    """
    search_results = await document_service.search_documents(
        payload.query, current_user
    )
    return search_results


@router.post("/chat", response_model=RAGChatResponse)
async def chat_with_documents(
    payload: RAGChatRequest,
    document_service: DocumentServiceDep,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Answers a question using retrieved document chunks as context.
    """
    return await document_service.answer_question(
        query=payload.query,
        current_user=current_user,
        top_k=payload.top_k,
    )

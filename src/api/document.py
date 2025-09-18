from fastapi import APIRouter, Depends, UploadFile, File
from ..core.dependencies import get_current_user, DocumentServiceDep
from ..models.auth import User
from ..schemas.document import DocumentUploadResponse  # Import the response model


router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    document_service: DocumentServiceDep,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
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

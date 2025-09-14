from fastapi import APIRouter, Depends, UploadFile, File, HTTPException



router = APIRouter()




@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass
    # try:
    #     # Read file content
    #     content = await file.read()
        
    #     # Extract text
    #     text = extract_text_from_file(content, file.filename)
    #     if not text.strip():
    #         raise HTTPException(status_code=400, detail="Could not extract text from file")
        
    #     # Chunk the text
    #     chunks = chunk_text(text)
        
    #     # Get user's collection
    #     collection = get_or_create_collection(current_user.id)
        
    #     # Generate embeddings and store in ChromaDB
    #     doc_id = str(uuid.uuid4())
    #     ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
    #     collection.add(
    #         documents=chunks,
    #         ids=ids,
    #         metadatas=[{"filename": file.filename, "chunk_id": i} for i in range(len(chunks))]
    #     )
        
    #     # Save document info to database
    #     db_doc = Document(
    #         filename=file.filename,
    #         user_id=current_user.id,
    #         doc_id=doc_id
    #     )
    #     db.add(db_doc)
    #     db.commit()
        
    #     return {"message": f"Document '{file.filename}' uploaded successfully", "chunks": len(chunks)}
    
    # except Exception as e:
    #     logger.error(f"Error uploading document: {e}")
    #     raise HTTPException(status_code=500, detail="Error processing document")

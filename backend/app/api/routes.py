"""
API routes for document upload, query, and decision mode.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import VectorDBService
from app.services.rag_service import RAGService
from app.services.decision_mode_service import DecisionModeService
from app.core.config import settings

router = APIRouter()

# Initialize services
doc_processor = DocumentProcessor()
embedding_service = EmbeddingService()
vector_db = VectorDBService()
rag_service = RAGService()
decision_service = DecisionModeService()


# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = "default"


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    metadata: dict


class DecisionRequest(BaseModel):
    query: str
    mode: str  # risk_analysis, revenue_analysis, clause_extraction, summary
    user_id: Optional[str] = "default"


class DecisionResponse(BaseModel):
    mode: str
    result: str
    structured_data: Optional[dict]
    metadata: dict


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = "default"
):
    """
    Upload and process a document.
    
    Supported formats: PDF, DOCX, TXT
    """
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Save file temporarily
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    file_path = uploads_dir / file.filename
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        # Process document
        chunks = doc_processor.process_document(
            file_path=str(file_path),
            filename=file.filename,
            user_id=user_id
        )
        
        # Generate embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings(texts)
        
        # Store in vector DB (chunks already have metadata structure)
        chunks_with_metadata = [
            {"metadata": chunk}
            for chunk in chunks
        ]
        vector_db.store_documents(chunks_with_metadata, embeddings, user_id)
        
        # Clean up temp file (optional - you might want to keep it)
        # os.remove(file_path)
        
        return {
            "message": "Document processed successfully",
            "filename": file.filename,
            "chunks_created": len(chunks),
            "user_id": user_id
        }
    
    except Exception as e:
        # Clean up on error
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query uploaded documents using RAG.
    """
    try:
        result = rag_service.query(
            question=request.question,
            user_id=request.user_id
        )
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/decision-mode", response_model=DecisionResponse)
async def decision_mode(request: DecisionRequest):
    """
    Process decision mode queries (risk analysis, revenue analysis, etc.).
    
    Modes:
    - risk_analysis: Identify risks and liabilities
    - revenue_analysis: Analyze revenue trends
    - clause_extraction: Extract legal clauses
    - summary: Executive summary
    """
    valid_modes = ["risk_analysis", "revenue_analysis", "clause_extraction", "summary"]
    
    if request.mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Valid modes: {valid_modes}"
        )
    
    try:
        result = decision_service.process_decision_query(
            query=request.query,
            mode=request.mode,
            user_id=request.user_id
        )
        return DecisionResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing decision query: {str(e)}")


@router.get("/documents")
async def list_documents(user_id: str = "default"):
    """
    List uploaded documents for a user.
    (Simplified - in production, you'd track this in a database)
    """
    # This is a placeholder - in production, you'd query a database
    return {
        "message": "Document listing not fully implemented yet",
        "user_id": user_id,
        "note": "In production, this would query a database to list user's documents"
    }

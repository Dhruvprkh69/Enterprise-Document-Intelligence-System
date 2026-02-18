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
from app.services.auth_service import AuthService
from app.core.config import settings

router = APIRouter()

# Initialize services
doc_processor = DocumentProcessor()
embedding_service = EmbeddingService()
vector_db = VectorDBService()
rag_service = RAGService()
decision_service = DecisionModeService()


# Request/Response Models
class AuthRequest(BaseModel):
    token: str


class AuthResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = "default"
    token: Optional[str] = None  # Google OAuth token (optional for backward compatibility)


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    metadata: dict


class DecisionRequest(BaseModel):
    query: str
    mode: str  # risk_analysis, revenue_analysis, clause_extraction, summary
    user_id: Optional[str] = "default"
    token: Optional[str] = None  # Google OAuth token (optional for backward compatibility)


class DecisionResponse(BaseModel):
    mode: str
    result: str
    structured_data: Optional[dict]
    metadata: dict


class ClearDocumentsRequest(BaseModel):
    user_id: Optional[str] = "default"
    filename: Optional[str] = None
    token: Optional[str] = None  # Google OAuth token (optional for backward compatibility)


class ClearDocumentsResponse(BaseModel):
    message: str
    user_id: str
    filename: Optional[str] = None
    chunks_deleted: int


@router.post("/auth/verify", response_model=AuthResponse)
async def verify_auth(request: AuthRequest):
    """
    Verify Google OAuth token and return user info.
    For CV demo - simple authentication layer.
    """
    try:
        user_info = AuthService.verify_google_token(request.token)
        return AuthResponse(**user_info)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = "default",
    token: Optional[str] = None
):
    """
    Upload and process a document.
    
    Supported formats: PDF, DOCX, TXT
    """
    # Extract user_id from token if provided
    if token:
        try:
            user_info = AuthService.verify_google_token(token)
            user_id = user_info['user_id']
        except:
            pass  # Fallback to provided user_id
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed: {settings.allowed_extensions_list}"
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


@router.post("/documents/clear", response_model=ClearDocumentsResponse)
async def clear_documents(request: ClearDocumentsRequest):
    """
    Clear (delete) all stored vector chunks for a user_id.
    Optionally scope deletion to a specific filename.

    This prevents "old PDFs leaking into sources" when re-uploading new documents under the same user_id.
    """
    # Extract user_id from token if provided
    user_id = request.user_id or "default"
    if request.token:
        try:
            user_info = AuthService.verify_google_token(request.token)
            user_id = user_info["user_id"]
        except:
            pass  # Fallback to provided user_id

    try:
        deleted = vector_db.delete_documents(user_id=user_id, filename=request.filename)
        return ClearDocumentsResponse(
            message="Documents cleared successfully",
            user_id=user_id,
            filename=request.filename,
            chunks_deleted=deleted
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query uploaded documents using RAG.
    """
    # Extract user_id from token if provided
    user_id = request.user_id
    if request.token:
        try:
            user_info = AuthService.verify_google_token(request.token)
            user_id = user_info['user_id']
        except:
            pass  # Fallback to provided user_id
    
    try:
        result = rag_service.query(
            question=request.question,
            user_id=user_id
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
    
    # Extract user_id from token if provided
    user_id = request.user_id
    if request.token:
        try:
            user_info = AuthService.verify_google_token(request.token)
            user_id = user_info['user_id']
        except:
            pass  # Fallback to provided user_id
    
    try:
        result = decision_service.process_decision_query(
            query=request.query,
            mode=request.mode,
            user_id=user_id
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

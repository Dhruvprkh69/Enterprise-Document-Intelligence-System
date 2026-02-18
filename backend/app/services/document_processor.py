"""
Document processing service.
Handles file upload, text extraction, and chunking.
"""
import os
from typing import List, Dict
from pathlib import Path
import PyPDF2
import pdfplumber
from docx import Document
from app.core.config import settings


class DocumentProcessor:
    """Processes documents: extract text and create chunks."""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.uploads_dir = Path("uploads")
        self.uploads_dir.mkdir(exist_ok=True)
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract text from different file types.
        
        Args:
            file_path: Path to the file
            file_type: File extension (.pdf, .docx, .txt)
        
        Returns:
            Extracted text content
        """
        text = ""
        
        if file_type == ".pdf":
            # Try pdfplumber first (better for complex PDFs)
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = "\n".join([page.extract_text() or "" for page in pdf.pages])
            except:
                # Fallback to PyPDF2
                with open(file_path, "rb") as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = "\n".join([page.extract_text() for page in pdf_reader.pages])
        
        elif file_type == ".docx":
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        elif file_type == ".txt":
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
        
        return text.strip()
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            metadata: Additional metadata to attach to each chunk
        
        Returns:
            List of chunks with metadata
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Extract chunk
            chunk_text = text[start:end]
            
            # Create chunk metadata
            chunk_metadata = {
                "chunk_id": chunk_id,
                "start_char": start,
                "end_char": end,
                "text": chunk_text
            }
            
            # Add original metadata if provided
            if metadata:
                chunk_metadata.update(metadata)
            
            chunks.append(chunk_metadata)
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap
            chunk_id += 1
        
        return chunks
    
    def process_document(self, file_path: str, filename: str, user_id: str = "default") -> List[Dict]:
        """
        Complete document processing pipeline.
        
        Args:
            file_path: Path to uploaded file
            filename: Original filename
            user_id: User identifier (for multi-tenancy)
        
        Returns:
            List of processed chunks with metadata
        """
        # Get file type
        file_type = Path(filename).suffix.lower()
        
        if file_type not in settings.allowed_extensions_list:
            raise ValueError(f"File type {file_type} not allowed")
        
        # Extract text
        text = self.extract_text(file_path, file_type)
        
        if not text:
            raise ValueError("No text extracted from document")
        
        # Prepare metadata
        metadata = {
            "filename": filename,
            "user_id": user_id,
            "file_type": file_type,
            "total_chars": len(text)
        }
        
        # Create chunks
        chunks = self.chunk_text(text, metadata)
        
        return chunks

"""
Vector database service.
Handles storage and retrieval of embeddings.
Supports Chroma (local) and can be extended for Pinecone (cloud).
"""
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.services.embedding_service import EmbeddingService


class VectorDBService:
    """Manages vector database operations."""
    
    def __init__(self):
        self.db_type = settings.VECTOR_DB_TYPE
        self.embedding_service = EmbeddingService()
        
        if self.db_type == "chroma":
            self._init_chroma()
        else:
            raise ValueError(f"Vector DB type {self.db_type} not implemented yet")
    
    def _init_chroma(self):
        """Initialize ChromaDB."""
        self.client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def store_documents(self, chunks: List[Dict], embeddings: List[List[float]], user_id: str = "default"):
        """
        Store document chunks with embeddings in vector DB.
        
        Args:
            chunks: List of chunk dictionaries with metadata
            embeddings: List of embedding vectors
            user_id: User identifier for multi-tenancy
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings count mismatch")
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = f"{user_id}_{chunk['metadata'].get('filename', 'doc')}_{chunk['metadata'].get('chunk_id', i)}"
            ids.append(chunk_id)
            
            # Store text
            documents.append(chunk['metadata']['text'])
            
            # Store metadata
            metadata = {
                **chunk['metadata'],
                "user_id": user_id
            }
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def search(self, query: str, top_k: int = None, user_id: str = "default", filter_dict: Dict = None) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            user_id: User identifier for filtering
            filter_dict: Additional filters
        
        Returns:
            List of similar chunks with metadata and scores
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_single_embedding(query)
        
        # Prepare filters
        where = {"user_id": user_id}
        if filter_dict:
            where.update(filter_dict)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def delete_user_documents(self, user_id: str):
        """Delete all documents for a user. Returns number of chunks deleted."""
        return self.delete_documents(user_id=user_id)

    def delete_documents(self, user_id: str = "default", filename: Optional[str] = None) -> int:
        """
        Delete chunks for a given user, optionally scoped to a filename.

        We query IDs first (so we can return a count) and then delete by IDs
        for maximum compatibility across Chroma versions.
        """
        where: Dict[str, Any] = {"user_id": user_id}
        if filename:
            where["filename"] = filename

        try:
            existing = self.collection.get(where=where, include=[])
            ids = existing.get("ids") or []
            if not ids:
                return 0

            # Chroma accepts either ids=[...] or where=... depending on version/config;
            # deleting by ids is safest once we have them.
            self.collection.delete(ids=ids)
            return len(ids)
        except Exception:
            # Fail closed: if delete fails, report 0 (caller can decide how to handle).
            return 0

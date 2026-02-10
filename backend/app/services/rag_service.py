"""
RAG (Retrieval-Augmented Generation) service.
Combines document retrieval with LLM generation.
"""
from typing import List, Dict
from app.services.vector_db_service import VectorDBService
from app.services.llm_service import LLMService
from app.core.config import settings


class RAGService:
    """Main RAG service that orchestrates retrieval and generation."""
    
    def __init__(self):
        self.vector_db = VectorDBService()
        self.llm = LLMService()
    
    def query(self, question: str, user_id: str = "default", top_k: int = None) -> Dict:
        """
        Process a query: retrieve relevant chunks and generate answer.
        
        Args:
            question: User's question
            user_id: User identifier
            top_k: Number of chunks to retrieve
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.vector_db.search(
            query=question,
            top_k=top_k or settings.TOP_K_RESULTS,
            user_id=user_id
        )
        
        if not retrieved_chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents.",
                "sources": [],
                "metadata": {
                    "chunks_retrieved": 0
                }
            }
        
        # Step 2: Build context from retrieved chunks
        context = self._build_context(retrieved_chunks)
        
        # Step 3: Create prompt with context
        prompt = self._create_rag_prompt(question, context)
        
        # Step 4: Generate answer using LLM
        answer = self.llm.generate_response(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for factual answers
            max_tokens=1500
        )
        
        # Step 5: Format sources with citations
        sources = self._format_sources(retrieved_chunks)
        
        return {
            "answer": answer,
            "sources": sources,
            "metadata": {
                "chunks_retrieved": len(retrieved_chunks),
                "question": question
            }
        }
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            
            context_parts.append(f"[Source {i} - {filename}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _create_rag_prompt(self, question: str, context: str) -> str:
        """Create prompt for RAG with context."""
        prompt = f"""You are a helpful assistant that answers questions based on the provided document context.

Context from documents:
{context}

Question: {question}

Instructions:
1. Answer the question using ONLY the information from the context above.
2. If the context doesn't contain enough information, say so clearly.
3. Be specific and cite which source (Source 1, Source 2, etc.) you're using.
4. If you're not sure, say "I'm not certain, but based on the documents..."

Answer:"""
        return prompt
    
    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Format sources for citation."""
        sources = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            sources.append({
                "source_id": i,
                "filename": metadata.get('filename', 'Unknown'),
                "chunk_id": metadata.get('chunk_id', 0),
                "text_preview": chunk.get('text', '')[:200] + "...",
                "relevance_score": 1 - chunk.get('distance', 1.0) if chunk.get('distance') else None
            })
        return sources

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
        # Determine if this is a complex question requiring more context
        is_complex = self._is_complex_question(question)
        effective_top_k = top_k or (settings.TOP_K_COMPLEX if is_complex else settings.TOP_K_RESULTS)
        
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.vector_db.search(
            query=question,
            top_k=effective_top_k,
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
        
        # Step 3: Create prompt with context (enhanced for calculations and inference)
        prompt = self._create_rag_prompt(question, context, is_complex)
        
        # Step 4: Generate answer using LLM (adjust temperature for complex questions)
        answer = self.llm.generate_response(
            prompt=prompt,
            temperature=0.2 if is_complex else 0.3,  # Lower temperature for complex reasoning
            max_tokens=2000 if is_complex else 1500  # More tokens for complex answers
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
        """Build context string from retrieved chunks, grouping by document."""
        # Group chunks by filename for better organization
        chunks_by_file = {}
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            if filename not in chunks_by_file:
                chunks_by_file[filename] = []
            chunks_by_file[filename].append(chunk)
        
        # Build context grouped by file
        context_parts = []
        source_counter = 1
        
        for filename, file_chunks in chunks_by_file.items():
            context_parts.append(f"\n=== Document: {filename} ===\n")
            for chunk in file_chunks:
                text = chunk.get('text', '')
                context_parts.append(f"[Source {source_counter} - {filename}]\n{text}\n")
                source_counter += 1
        
        return "\n".join(context_parts)
    
    def _is_complex_question(self, question: str) -> bool:
        """Determine if question requires complex reasoning."""
        complex_keywords = [
            'calculate', 'compute', 'ratio', 'percentage', 'margin', 'compare',
            'relationship', 'correlation', 'impact', 'analyze', 'inference',
            'why', 'how', 'explain', 'relationship between', 'connect'
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in complex_keywords)
    
    def _create_rag_prompt(self, question: str, context: str, is_complex: bool = False) -> str:
        """Create prompt for RAG with context, enhanced for calculations and inference."""
        
        base_instructions = """You are a helpful assistant that answers questions based on the provided document context.

Context from documents:
{context}

Question: {question}

Instructions:
1. Answer the question using ONLY the information from the context above.
2. If the context doesn't contain enough information, say so clearly.
3. Be specific and cite which source (Source 1, Source 2, etc.) you're using.
4. If you're not sure, say "I'm not certain, but based on the documents..."
"""
        
        calculation_instructions = """
5. **FOR CALCULATIONS**: If the question asks for calculations (percentages, ratios, margins, etc.):
   - First, identify ALL relevant numbers from the context
   - Extract the numbers clearly (e.g., "Revenue: ₹X crores, Profit: ₹Y crores")
   - Perform the calculation step-by-step
   - Show your work: "Calculation: (Y / X) × 100 = Z%"
   - If numbers are in different sources, combine them for calculation
   - Always verify your calculation is correct
"""
        
        inference_instructions = """
5. **FOR COMPLEX/INFERENCE QUESTIONS**: If the question requires analysis, comparison, or connecting different sections:
   - Read through ALL provided sources carefully
   - Look for relationships between different pieces of information
   - Connect information from multiple sources if needed
   - Provide reasoning for your answer
   - If information spans multiple sections, synthesize them together
   - Explain the connection or relationship clearly
"""
        
        if is_complex:
            # Check if it's a calculation question
            question_lower = question.lower()
            calc_keywords = ['calculate', 'compute', 'ratio', 'percentage', 'margin', 'divide', 'multiply']
            is_calculation = any(keyword in question_lower for keyword in calc_keywords)
            
            if is_calculation:
                instructions = base_instructions + calculation_instructions
            else:
                instructions = base_instructions + inference_instructions
        else:
            instructions = base_instructions
        
        instructions += "\nAnswer:"
        
        prompt = instructions.format(context=context, question=question)
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

"""
Decision Mode service for business intelligence tasks.
Handles specialized queries: risk analysis, revenue analysis, clause extraction, etc.
"""
from typing import Dict, List
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.core.config import settings


class DecisionModeService:
    """Handles decision mode queries with specialized prompts."""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.llm = LLMService()
    
    def process_decision_query(
        self,
        query: str,
        mode: str,
        user_id: str = "default"
    ) -> Dict:
        """
        Process a decision mode query.
        
        Args:
            query: User's query
            mode: Decision mode type (risk_analysis, revenue_analysis, clause_extraction, summary)
            user_id: User identifier
        
        Returns:
            Structured response based on mode
        """
        # First, retrieve relevant chunks
        retrieved_chunks = self.rag_service.vector_db.search(
            query=query,
            top_k=settings.TOP_K_RESULTS * 2,  # Get more chunks for analysis
            user_id=user_id
        )
        
        if not retrieved_chunks:
            return {
                "mode": mode,
                "result": "No relevant information found in documents.",
                "structured_data": None
            }
        
        # Build context
        context = self._build_context(retrieved_chunks)
        
        # Get mode-specific prompt
        prompt = self._get_mode_prompt(mode, query, context)
        
        # Generate response
        response = self.llm.generate_response(
            prompt=prompt,
            temperature=0.2,  # Lower temperature for structured outputs
            max_tokens=2000
        )
        
        # Format response based on mode
        formatted_response = self._format_response(mode, response, retrieved_chunks)
        
        return formatted_response
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context from chunks."""
        context_parts = []
        for chunk in chunks:
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            context_parts.append(f"[{filename}]\n{text}\n")
        return "\n".join(context_parts)
    
    def _get_mode_prompt(self, mode: str, query: str, context: str) -> str:
        """Get mode-specific prompt template."""
        
        mode_prompts = {
            "risk_analysis": f"""Analyze the following document context and identify all risks, liabilities, and potential issues.

Context:
{context}

Query: {query}

Provide a structured analysis with:
1. List of identified risks (with severity: High/Medium/Low)
2. Description of each risk
3. Affected parties or areas
4. Potential impact
5. Recommendations (if applicable)

Format your response clearly with numbered items.""",

            "revenue_analysis": f"""Analyze the following document context for revenue trends, financial performance, and business metrics.

Context:
{context}

Query: {query}

Provide a structured analysis with:
1. Revenue trends (increasing/decreasing/stable)
2. Key factors affecting revenue
3. Specific numbers or percentages mentioned
4. Time periods covered
5. Recommendations or insights

Format your response clearly with numbered items.""",

            "clause_extraction": f"""Extract all legal clauses, obligations, deadlines, and important terms from the following document context.

Context:
{context}

Query: {query}

Provide a structured extraction with:
1. Clause type (e.g., Payment Terms, Termination, Liability, etc.)
2. Description of the clause
3. Parties involved
4. Deadlines or dates (if any)
5. Key obligations or requirements

Format your response clearly with numbered items.""",

            "summary": f"""Provide a comprehensive executive summary of the following document context.

Context:
{context}

Query: {query}

Create a summary that includes:
1. Main topics and themes
2. Key points and findings
3. Important numbers or statistics
4. Conclusions or recommendations
5. Action items (if any)

Format your response clearly with numbered sections."""
        }
        
        return mode_prompts.get(mode, f"Analyze the following context and answer the query:\n\nContext:\n{context}\n\nQuery: {query}")
    
    def _format_response(self, mode: str, response: str, chunks: List[Dict]) -> Dict:
        """Format response with metadata."""
        # Extract source filenames
        sources = list(set([
            chunk.get('metadata', {}).get('filename', 'Unknown')
            for chunk in chunks
        ]))
        
        return {
            "mode": mode,
            "result": response,
            "structured_data": {
                "sources": sources,
                "chunks_analyzed": len(chunks)
            },
            "metadata": {
                "mode": mode,
                "sources_count": len(sources)
            }
        }

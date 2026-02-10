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
        # First, retrieve relevant chunks (use more for decision mode analysis)
        retrieved_chunks = self.rag_service.vector_db.search(
            query=query,
            top_k=settings.TOP_K_COMPLEX,  # Get more chunks for comprehensive analysis
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

**IMPORTANT:**
- Focus ONLY on risks mentioned in the provided context
- Do NOT add risks from other documents or general knowledge
- If the query asks about specific risks (e.g., "cybersecurity risk"), focus on that
- Extract exact financial impact numbers if mentioned (e.g., "up to ₹50 crores")
- List ALL mitigation strategies mentioned in the context

Provide a structured analysis with:
1. List of identified risks (with severity: High/Medium/Low) - ONLY from the context
2. Description of each risk - use exact wording from context when possible
3. Affected parties or areas - extract from context
4. Potential impact - include specific numbers if mentioned
5. Recommendations (if applicable) - list ALL mitigation strategies from context

Format your response clearly with numbered items.""",

            "revenue_analysis": f"""Analyze the following document context for revenue trends, financial performance, and business metrics.

Context:
{context}

Query: {query}

**IMPORTANT FOR CALCULATIONS:**
- If you need to calculate percentages, margins, ratios, or growth rates:
  - Extract ALL relevant numbers from the context
  - Show your calculation step-by-step
  - Example: "Net Profit Margin = (Net Profit / Total Revenue) × 100 = (₹27.6 crores / ₹201.8 crores) × 100 = 13.7%"
  - If numbers are in different sources, combine them for calculation
  - Always verify your math is correct

Provide a structured analysis with:
1. Revenue trends (increasing/decreasing/stable) - include specific numbers and percentages
2. Key factors affecting revenue - be specific with numbers
3. Specific numbers or percentages mentioned - extract ALL financial figures
4. Time periods covered - be precise with dates
5. Recommendations or insights - based on the data provided

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

**IMPORTANT:**
- Include ALL key numbers, percentages, and statistics from the context
- Extract information from ALL provided sources
- If the query asks for specific information (e.g., "business verticals"), make sure to include it
- Connect related information from different sources if needed

Create a summary that includes:
1. Main topics and themes - be comprehensive
2. Key points and findings - include specific numbers and percentages
3. Important numbers or statistics - extract ALL financial figures, dates, percentages
4. Conclusions or recommendations - based on the data provided
5. Action items (if any) - extract from context

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

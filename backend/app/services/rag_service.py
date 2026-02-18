"""
RAG (Retrieval-Augmented Generation) service.
Combines document retrieval with LLM generation.
Enhanced with NLP analysis, intent detection, and ChatGPT-like explanations.
"""
from typing import List, Dict, Optional
from app.services.vector_db_service import VectorDBService
from app.services.llm_service import LLMService
from app.services.nlp_service import NLPService
from app.core.config import settings


class RAGService:
    """Main RAG service that orchestrates retrieval and generation."""
    
    def __init__(self):
        self.vector_db = VectorDBService()
        self.llm = LLMService()
        self.nlp = NLPService()
    
    def query(self, question: str, user_id: str = "default", top_k: int = None) -> Dict:
        """
        Process a query: retrieve relevant chunks and generate answer.
        Enhanced with NLP analysis, intent detection, and ChatGPT-like explanations.
        
        Args:
            question: User's question
            user_id: User identifier
            top_k: Number of chunks to retrieve
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Step 0: Analyze question with NLP
        query_analysis = self.nlp.analyze_question(question)
        needs_explanation = query_analysis["needs_explanation"]
        user_level = query_analysis["user_level"]
        intent = query_analysis["intent"]
        is_confused = query_analysis["is_confused"]
        key_terms = query_analysis["key_terms"]
        
        # Determine if this is a complex question
        is_complex = (
            needs_explanation or 
            intent in ["analytical", "explanatory", "calculative"] or
            query_analysis["question_type"] in ["why", "how"]
        )
        
        effective_top_k = top_k or (settings.TOP_K_COMPLEX if is_complex else settings.TOP_K_RESULTS)
        
        # Step 1: Retrieve relevant chunks (with query expansion for better retrieval)
        query_variations = self.nlp.expand_query(question)
        retrieved_chunks = self.vector_db.search(
            query=question,
            top_k=effective_top_k,
            user_id=user_id
        )
        
        if not retrieved_chunks:
            # Even if no chunks, provide helpful response
            if needs_explanation and key_terms:
                return {
                    "answer": self._generate_general_knowledge_response(question, key_terms, user_level),
                    "sources": [],
                    "metadata": {
                        "chunks_retrieved": 0,
                        "query_analysis": query_analysis
                    }
                }
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents. Could you rephrase your question or upload relevant documents?",
                "sources": [],
                "metadata": {
                    "chunks_retrieved": 0,
                    "query_analysis": query_analysis
                }
            }
        
        # Step 2: Build context from retrieved chunks
        context = self._build_context(retrieved_chunks)
        
        # Step 3: Create enhanced prompt with intent detection and Chain-of-Thought
        prompt = self._create_enhanced_rag_prompt(
            question=question,
            context=context,
            query_analysis=query_analysis
        )
        
        # Step 4: Generate answer using LLM
        # Adjust temperature and tokens based on user needs
        temperature = 0.2 if is_complex else (0.4 if user_level == "beginner" else 0.3)
        max_tokens = 2500 if needs_explanation else (2000 if is_complex else 1500)
        
        answer = self.llm.generate_response(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Step 5: Format sources with citations
        sources = self._format_sources(retrieved_chunks)
        
        return {
            "answer": answer,
            "sources": sources,
            "metadata": {
                "chunks_retrieved": len(retrieved_chunks),
                "question": question,
                "query_analysis": query_analysis
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
    
    def _generate_general_knowledge_response(self, question: str, key_terms: List[str], user_level: str) -> str:
        """Generate response using general knowledge when documents don't have info."""
        prompt = f"""You are a helpful assistant. The user asked: "{question}"

The user seems to be asking about: {', '.join(key_terms)}

However, I don't have specific information about this in the uploaded documents. 

Please provide a helpful general explanation that:
1. Acknowledges that the specific document context isn't available
2. Provides general knowledge about the topic
3. Uses {"simple, beginner-friendly language" if user_level == "beginner" else "appropriate technical language"}
4. Suggests that uploading relevant documents would help provide more specific answers

Be concise but informative."""
        
        try:
            return self.llm.generate_response(prompt, temperature=0.4, max_tokens=800)
        except:
            return f"I couldn't find specific information about '{', '.join(key_terms)}' in the uploaded documents. Could you upload relevant documents or rephrase your question?"
    
    def _create_enhanced_rag_prompt(self, question: str, context: str, query_analysis: Dict) -> str:
        """Create enhanced prompt with Chain-of-Thought, intent detection, and layered explanations."""
        
        intent = query_analysis["intent"]
        user_level = query_analysis["user_level"]
        question_type = query_analysis["question_type"]
        is_confused = query_analysis["is_confused"]
        needs_explanation = query_analysis["needs_explanation"]
        key_terms = query_analysis.get("key_terms", [])
        
        # Base role and context
        role_instruction = f"""You are an expert assistant helping users understand their documents. 
The user is asking: "{question}"

**User Context:**
- Question Type: {question_type}
- Intent: {intent}
- Knowledge Level: {user_level}
- Needs Explanation: {needs_explanation}
- Key Terms: {', '.join(key_terms) if key_terms else 'N/A'}
"""
        
        if is_confused:
            role_instruction += "\n⚠️ The user seems confused or needs clarification. Be extra clear and patient.\n"
        
        # Document context
        context_section = f"""
**Document Context:**
{context}

**IMPORTANT:** Use the information from the documents above to answer the question. Cite sources (Source 1, Source 2, etc.) when referencing specific information.
"""
        
        # Instructions based on intent and user level
        instructions = self._get_instructions_for_intent(intent, question_type, user_level, needs_explanation)
        
        # Chain-of-Thought reasoning
        cot_instruction = """
**Think step-by-step:**
1. First, understand what the user is really asking
2. Identify relevant information from the context
3. If needed, explain key terms or concepts
4. Synthesize information from multiple sources if required
5. Provide a clear, structured answer
"""
        
        # Format instructions
        format_instruction = self._get_format_instructions(user_level, needs_explanation)
        
        # Combine all parts
        prompt = f"""{role_instruction}

{context_section}

{instructions}

{cot_instruction}

{format_instruction}

**Now provide your answer:**"""
        
        return prompt
    
    def _get_instructions_for_intent(self, intent: str, question_type: str, user_level: str, needs_explanation: bool) -> str:
        """Get specific instructions based on user intent."""
        
        base = """Answer the question using the document context provided above.

Critical rules:
1. Do NOT invent numbers, names, dates, or facts that are not explicitly present in the Document Context.
2. If the Document Context does not contain the requested information, say so clearly.
3. Do NOT infer "profitability" of a segment from revenue or growth rate alone. Only discuss segment profitability/margins if segment-level profit or margin data is present in the Document Context.
4. If multiple documents are present, prefer the most relevant one and avoid mixing unrelated documents into the reasoning."""
        
        if intent == "explanatory" or needs_explanation:
            return f"""{base}

**EXPLANATION MODE - Provide detailed, comprehensive explanation:**

1. **Start with a simple summary** (1-2 sentences) - what is this about?
2. **Provide detailed explanation:**
   - Define key terms if the user might not know them
   - Explain the concept clearly
   - Use examples or analogies if helpful
   - Connect related information from different sources
3. **Reference the documents:**
   - Cite specific sources (Source 1, Source 2, etc.)
   - Include relevant numbers, dates, or facts from the documents
4. **Add context:**
   - Explain why this matters
   - Connect to broader concepts if relevant
   - Use {"simple, beginner-friendly language" if user_level == "beginner" else "appropriate technical language"}

**Example structure:**
- **Simple Summary:** [One-line answer]
- **Detailed Explanation:** [Comprehensive explanation with examples]
- **From Documents:** [Specific information from sources]
- **Why It Matters:** [Context and implications]"""
        
        elif intent == "analytical":
            return f"""{base}

**ANALYSIS MODE - Provide thorough analysis:**

1. **Identify all relevant information** from the context
2. **Analyze relationships** between different pieces of information
3. **Compare and contrast** if multiple sources discuss similar topics
4. **Draw connections** between different sections
5. **Provide reasoning** for your conclusions
6. **Cite sources** for each piece of information

Structure your answer with clear sections and reasoning."""
        
        elif intent == "calculative":
            return f"""{base}

**CALCULATION MODE - Show your work:**

1. **Identify ALL relevant numbers** from the context
2. **Extract numbers clearly** (e.g., "Revenue: ₹X crores, Profit: ₹Y crores")
3. **Show calculation steps:**
   - Step 1: [What you're calculating]
   - Step 2: [Formula/process]
   - Step 3: [Calculation]
   - Step 4: [Result]
4. **Verify your calculation** is correct
5. **Explain what the result means** in context"""
        
        elif intent == "factual":
            return f"""{base}

**FACTUAL MODE - Provide clear, direct answer:**

1. Answer directly and concisely
2. Cite the specific source (Source 1, Source 2, etc.)
3. Include relevant details (numbers, dates, names)
4. If multiple sources have the same info, mention all sources"""
        
        else:
            return f"""{base}

Provide a clear, well-structured answer that:
- Directly addresses the question
- Uses information from the documents
- Cites sources appropriately
- Is {"simple and easy to understand" if user_level == "beginner" else "appropriately detailed"}"""
    
    def _get_format_instructions(self, user_level: str, needs_explanation: bool) -> str:
        """Get formatting instructions based on user needs."""
        
        if needs_explanation:
            return """
**Format your answer:**
- Use clear sections with headers (## or **bold**)
- Use bullet points or numbered lists for clarity
- Include examples where helpful
- Use markdown formatting for better readability
- Make it easy to scan and understand"""
        else:
            return """
**Format your answer:**
- Be clear and concise
- Use bullet points if listing multiple items
- Cite sources clearly (Source 1, Source 2, etc.)
- Use proper formatting for readability"""
    
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

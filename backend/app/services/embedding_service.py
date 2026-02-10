"""
Embedding service for generating vector embeddings.
Supports multiple providers: Gemini, Hugging Face.
"""
from typing import List
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Global model instance (singleton pattern - load once)
_hf_model = None


def _get_hf_model():
    """Get or create Hugging Face model instance (singleton)."""
    global _hf_model
    if _hf_model is None:
        print("Loading Hugging Face embedding model (all-MiniLM-L6-v2)... This may take a moment.")
        _hf_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Hugging Face model loaded successfully!")
    return _hf_model


class EmbeddingService:
    """Generates embeddings for text chunks."""
    
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY
        # Default to Hugging Face (more reliable, free, local)
        # Gemini can be enabled if API key is valid and model name is correct
        self.use_gemini = False  # Disabled by default due to model name issues
        
        # Initialize Hugging Face model (default) - uses singleton
        self.model = _get_hf_model()
        
        # Optional: Initialize Gemini if API key available and you want to use it
        # Note: Gemini embedding model names may vary, check latest docs
        if self.gemini_api_key and False:  # Set to True if you fix Gemini model name
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.use_gemini = True
                print("Gemini embeddings enabled")
            except Exception as e:
                print(f"Gemini initialization failed: {e}, using Hugging Face")
                self.use_gemini = False
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.use_gemini:
            return self._generate_gemini_embeddings(texts)
        else:
            return self._generate_hf_embeddings(texts)
    
    def _generate_gemini_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Gemini API."""
        embeddings = []
        for text in texts:
            try:
                # Try different Gemini embedding model names
                # Latest models: "models/embedding-001" or check Gemini docs
                result = genai.embed_content(
                    model="models/embedding-001",  # Updated model name
                    content=text,
                    task_type="retrieval_document"  # Specify task type
                )
                embeddings.append(result['embedding'])
            except Exception as e:
                print(f"Error generating Gemini embedding: {e}")
                # Fallback to HF if Gemini fails
                embeddings.append(self.model.encode(text).tolist())
        
        return embeddings
    
    def _generate_hf_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Hugging Face (local)."""
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            print(f"Error generating Hugging Face embeddings: {e}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.generate_embeddings([text])[0]

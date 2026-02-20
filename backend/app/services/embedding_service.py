"""
Embedding service for generating vector embeddings.
Uses Hugging Face Inference API (free, no local models, no API key needed).
"""
from typing import List
import requests
from app.core.config import settings


class EmbeddingService:
    """Generates embeddings for text chunks using Hugging Face Inference API."""
    
    def __init__(self):
        # Hugging Face Inference API - updated endpoint format
        self.api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        print("✓ Using Hugging Face Inference API for embeddings (free, no API key needed)")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Gemini API.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        return self._generate_hf_api_embeddings(texts)
    
    def _generate_hf_api_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Hugging Face Inference API (free, no API key)."""
        embeddings = []
        
        # Process one by one to avoid rate limits and handle model loading
        for text in texts:
            try:
                response = requests.post(
                    self.api_url,
                    json={"inputs": text},
                    headers={"Content-Type": "application/json"},
                    timeout=60  # Increased timeout for model loading
                )
                
                # Handle model loading (503) - wait and retry
                if response.status_code == 503:
                    # Model is loading, wait a bit and retry
                    import time
                    time.sleep(5)
                    response = requests.post(
                        self.api_url,
                        json={"inputs": text},
                        headers={"Content-Type": "application/json"},
                        timeout=60
                    )
                
                response.raise_for_status()
                result = response.json()
                
                # Handle response format
                if isinstance(result, list):
                    if isinstance(result[0], list):
                        embeddings.append(result[0])  # Nested list
                    else:
                        embeddings.append(result)  # Flat list
                else:
                    embeddings.append(result)
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    # Model still loading, use fallback or wait longer
                    raise Exception("Hugging Face model is loading. Please wait a moment and try again.")
                else:
                    print(f"Error generating Hugging Face embeddings: {e}")
                    raise Exception(f"Failed to generate embeddings: {str(e)}")
            except Exception as e:
                print(f"Error generating Hugging Face embeddings: {e}")
                raise Exception(f"Failed to generate embeddings: {str(e)}")
        
        return embeddings
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.generate_embeddings([text])[0]

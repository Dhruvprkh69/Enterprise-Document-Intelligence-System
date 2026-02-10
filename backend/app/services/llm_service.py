"""
LLM service for generating responses.
Supports Groq API (primary) and Gemini API (fallback).
"""
from typing import Optional
from groq import Groq
import google.generativeai as genai
from app.core.config import settings


class LLMService:
    """Handles LLM API calls for text generation."""
    
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.gemini_api_key = settings.GEMINI_API_KEY
        
        # Initialize Groq client
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        # Initialize Gemini if available
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
    
    def generate_response(
        self,
        prompt: str,
        model: str = "groq",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response using LLM.
        
        Args:
            prompt: Input prompt
            model: "groq" or "gemini"
            temperature: Creativity level (0-1)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        """
        if model == "groq":
            return self._generate_groq_response(prompt, temperature, max_tokens)
        elif model == "gemini" and self.gemini_model:
            return self._generate_gemini_response(prompt, temperature)
        else:
            # Fallback to Groq
            return self._generate_groq_response(prompt, temperature, max_tokens)
    
    def _generate_groq_response(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate response using Groq API (Llama 3.3 - latest)."""
        try:
            # Try latest model first, fallback to alternatives
            models_to_try = [
                "llama-3.3-70b-versatile",  # Latest model
                "llama-3.1-8b-instant",      # Fast alternative
                "mixtral-8x7b-32768"         # Alternative model
            ]
            
            last_error = None
            for model_name in models_to_try:
                try:
                    chat_completion = self.groq_client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        model=model_name,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    return chat_completion.choices[0].message.content
                except Exception as e:
                    last_error = e
                    continue  # Try next model
            
            # If all models fail, raise the last error
            raise Exception(f"Groq API error: {str(last_error)}")
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def _generate_gemini_response(self, prompt: str, temperature: float) -> str:
        """Generate response using Gemini API."""
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

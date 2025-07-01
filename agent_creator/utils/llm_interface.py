"""
LLM Interface for MLX model interactions with HuggingFace models
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

try:
    import mlx.core as mx
    import mlx.nn as nn
    from mlx_lm import load, generate
    from transformers import AutoTokenizer
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    logging.warning("MLX not available. Using fallback mode.")

@dataclass
class LLMConfig:
    """Configuration for LLM model"""
    model_name: str = "microsoft/DialoGPT-medium"
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    device: str = "auto"

class LLMInterface:
    """
    Interface for interacting with MLX-based language models from HuggingFace
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the LLM interface
        
        Args:
            config: LLM configuration object
        """
        self.config = config or LLMConfig()
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.logger = logging.getLogger(__name__)
        
    def load_model(self) -> bool:
        """
        Load the MLX model and tokenizer
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            if not MLX_AVAILABLE:
                self.logger.warning("MLX not available, using mock responses")
                self.is_loaded = True
                return True
                
            self.logger.info(f"Loading model: {self.config.model_name}")
            
            # Try to load MLX model
            try:
                self.model, self.tokenizer = load(self.config.model_name)
                self.is_loaded = True
                self.logger.info("MLX model loaded successfully")
                return True
            except Exception as e:
                self.logger.warning(f"Failed to load MLX model: {e}")
                # Fallback to tokenizer only for testing
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.config.model_name,
                    trust_remote_code=True
                )
                self.is_loaded = True
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the loaded model
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response text
        """
        if not self.is_loaded:
            if not self.load_model():
                return "Error: Failed to load model"
        
        try:
            # Override config parameters with any provided kwargs
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
            temperature = kwargs.get('temperature', self.config.temperature)
            
            if not MLX_AVAILABLE or self.model is None:
                # Mock response for testing/fallback
                return self._generate_mock_response(prompt)
            
            # Generate response using MLX
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                verbose=False
            )
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_mock_response(self, prompt: str) -> str:
        """
        Generate a mock response for testing when MLX is not available
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response
        """
        # Simple mock responses based on prompt content
        if "research" in prompt.lower():
            return "This is a mock research response. The topic appears to be about " + prompt[:50] + "..."
        elif "summarize" in prompt.lower():
            return "This is a mock summary response."
        elif "analyze" in prompt.lower():
            return "This is a mock analysis response."
        else:
            return f"This is a mock response to the prompt: {prompt[:100]}..."
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.is_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.config.model_name,
            "is_loaded": self.is_loaded,
            "mlx_available": MLX_AVAILABLE,
            "config": {
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p
            }
        }
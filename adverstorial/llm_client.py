"""LLM client abstraction for OpenAI and Anthropic."""

from abc import ABC, abstractmethod
from typing import List, Dict
import os


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, model: str):
        self.model = model
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            
        Returns:
            The generated text response.
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, model: str):
        super().__init__(model)
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """Anthropic API client."""
    
    def __init__(self, model: str):
        super().__init__(model)
        from anthropic import Anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response using Anthropic API."""
        # Anthropic expects system message separately
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        kwargs = {
            "model": self.model,
            "messages": conversation_messages,
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        if system_message:
            kwargs["system"] = system_message
        
        response = self.client.messages.create(**kwargs)
        return response.content[0].text


def create_client(system: str, model: str) -> LLMClient:
    """Factory function to create the appropriate LLM client.
    
    Args:
        system: Either 'openai' or 'anthropic'
        model: The model name to use
        
    Returns:
        An instance of the appropriate LLM client
    """
    system = system.lower()
    if system == "openai":
        return OpenAIClient(model)
    elif system == "anthropic":
        return AnthropicClient(model)
    else:
        raise ValueError(f"Unknown system: {system}. Must be 'openai' or 'anthropic'")

"""
LLM interface implementations for different providers.
"""

import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import asyncio


logger = logging.getLogger(__name__)


class LLMInterface(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        pass

    @abstractmethod
    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Async generate response from prompt."""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        pass


class OpenAIInterface(LLMInterface):
    """Interface for OpenAI models."""

    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.7, max_tokens: int = 4096):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None

        # Lazy load OpenAI client
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            logger.warning("OpenAI package not installed. Install with: pip install openai")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API."""
        if not self.client:
            return "OpenAI client not available"

        try:
            response = self.client.chat.completions.create(
                model=kwargs.get('model', self.model),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return f"Error: {e}"

    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Async generate using OpenAI API."""
        return await asyncio.to_thread(self.generate, prompt, **kwargs)

    def get_info(self) -> Dict[str, Any]:
        """Get OpenAI model info."""
        return {
            'provider': 'openai',
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }


class AnthropicInterface(LLMInterface):
    """Interface for Anthropic Claude models."""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229", temperature: float = 0.7, max_tokens: int = 4096):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None

        # Lazy load Anthropic client
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            logger.warning("Anthropic package not installed. Install with: pip install anthropic")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic API."""
        if not self.client:
            return "Anthropic client not available"

        try:
            response = self.client.messages.create(
                model=kwargs.get('model', self.model),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            return f"Error: {e}"

    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Async generate using Anthropic API."""
        return await asyncio.to_thread(self.generate, prompt, **kwargs)

    def get_info(self) -> Dict[str, Any]:
        """Get Anthropic model info."""
        return {
            'provider': 'anthropic',
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }


class LocalModelInterface(LLMInterface):
    """Interface for local models (Hugging Face, custom)."""

    def __init__(self, model_name: str, model_path: str, device: str = "auto"):
        self.model_name = model_name
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None

        # Try to load model
        self._load_model()

    def _load_model(self):
        """Load local model."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            logger.info(f"Loading local model: {self.model_name}")

            # Determine device
            if self.device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                device = self.device

            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.model_path
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=self.model_path,
                device_map=device if device == "cuda" else None
            )

            if device == "cpu":
                self.model = self.model.to(device)

            logger.info(f"Local model loaded on {device}")

        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            self.model = None
            self.tokenizer = None

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using local model."""
        if not self.model or not self.tokenizer:
            return "Local model not available (using fallback response)"

        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")

            # Generate
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
                do_sample=True
            )

            # Decode
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()

            return response

        except Exception as e:
            logger.error(f"Local model generation failed: {e}")
            return f"Error: {e}"

    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Async generate using local model."""
        return await asyncio.to_thread(self.generate, prompt, **kwargs)

    def get_info(self) -> Dict[str, Any]:
        """Get local model info."""
        return {
            'provider': 'local',
            'model': self.model_name,
            'model_path': self.model_path,
            'device': self.device,
            'loaded': self.model is not None
        }

    def shutdown(self):
        """Shutdown and cleanup model."""
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None


class DummyInterface(LLMInterface):
    """Dummy interface for testing without real models."""

    def __init__(self):
        pass

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate dummy response."""
        return f"[Dummy Model Response] Processed: {prompt[:100]}..."

    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Async dummy generate."""
        await asyncio.sleep(0.1)  # Simulate processing
        return self.generate(prompt, **kwargs)

    def get_info(self) -> Dict[str, Any]:
        """Get dummy model info."""
        return {
            'provider': 'dummy',
            'model': 'dummy-model',
            'note': 'This is a dummy model for testing'
        }

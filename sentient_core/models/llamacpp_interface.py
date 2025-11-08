"""
Llama.cpp Interface for Local LLM Inference.

Provides efficient local inference for GGUF quantized models (Qwen, Llama, etc.).
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class LlamaCppInterface:
    """
    Interface for llama.cpp-based local LLM inference.

    Optimized for:
    - Qwen 2.5 models
    - Llama 3 models
    - Phi-3 models
    - Other GGUF quantized models
    """

    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_threads: int = 4,
        n_gpu_layers: int = 0,
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Initialize llama.cpp interface.

        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_threads: Number of CPU threads
            n_gpu_layers: Number of layers to offload to GPU (if available)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.model_path = Path(model_path)
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_gpu_layers = n_gpu_layers
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Model instance
        self.llm = None
        self.model_loaded = False

        logger.info(f"LlamaCpp interface created for {self.model_path.name}")

    def initialize(self) -> bool:
        """
        Load model using llama.cpp.

        Returns:
            True if successful
        """
        try:
            from llama_cpp import Llama

            logger.info(f"Loading model: {self.model_path}")

            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )

            self.model_loaded = True
            logger.info("✓ Model loaded successfully")

            # Test generation
            test_output = self.llm("Test", max_tokens=5)
            logger.info("✓ Model test successful")

            return True

        except ImportError:
            logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            return False
        except FileNotFoundError:
            logger.error(f"Model file not found: {self.model_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Call initialize() first.")

        try:
            # Override default parameters with kwargs
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            temperature = kwargs.get('temperature', self.temperature)
            stop = kwargs.get('stop', ["\n\n", "User:", "###"])

            # Generate
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop,
                echo=False
            )

            # Extract generated text
            generated_text = output['choices'][0]['text']

            return generated_text.strip()

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"Error generating response: {str(e)}"

    async def generate_async(self, prompt: str, **kwargs) -> str:
        """
        Async version of generate.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        import asyncio
        return await asyncio.to_thread(self.generate, prompt, **kwargs)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat-style generation with message history.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional generation parameters

        Returns:
            Generated response
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")

        try:
            # Format messages into prompt
            prompt = self._format_chat_prompt(messages)

            # Generate response
            response = self.generate(prompt, **kwargs)

            return response

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Error in chat: {str(e)}"

    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Format chat messages into prompt.

        Args:
            messages: List of messages

        Returns:
            Formatted prompt string
        """
        # Qwen 2.5 chat format
        prompt = ""

        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'system':
                prompt += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif role == 'user':
                prompt += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == 'assistant':
                prompt += f"<|im_start|>assistant\n{content}<|im_end|>\n"

        # Add final assistant prompt
        prompt += "<|im_start|>assistant\n"

        return prompt

    def get_info(self) -> Dict[str, Any]:
        """
        Get model information.

        Returns:
            Dictionary with model info
        """
        info = {
            'provider': 'llamacpp',
            'model_path': str(self.model_path),
            'model_name': self.model_path.name,
            'loaded': self.model_loaded,
            'n_ctx': self.n_ctx,
            'n_threads': self.n_threads,
            'n_gpu_layers': self.n_gpu_layers
        }

        if self.llm:
            try:
                # Get model metadata if available
                info['metadata'] = {
                    'context_length': self.n_ctx
                }
            except Exception:
                pass

        return info

    def shutdown(self):
        """Cleanup model resources."""
        if self.llm:
            del self.llm
            self.llm = None
            self.model_loaded = False
            logger.info("Model unloaded")

    def __del__(self):
        """Cleanup on deletion."""
        self.shutdown()

    def __repr__(self) -> str:
        return f"<LlamaCppInterface(model={self.model_path.name}, loaded={self.model_loaded})>"

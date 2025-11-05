"""
Model manager for loading and managing AI models.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from .llm_interface import LLMInterface, OpenAIInterface, AnthropicInterface, LocalModelInterface


logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages AI models and provides a unified interface for inference.

    Supports multiple model providers:
    - Local models (Hugging Face, custom)
    - OpenAI API
    - Anthropic API
    - Other LLM providers
    """

    def __init__(self, config):
        """
        Initialize model manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.model_path = Path(config.model_path).expanduser()
        self.cache_dir = Path(config.cache_dir).expanduser()

        # Ensure directories exist
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Model registry
        self.models: Dict[str, LLMInterface] = {}
        self.active_model: Optional[LLMInterface] = None

        # Model metadata
        self.model_info: Dict[str, Dict[str, Any]] = {}

        logger.info("ModelManager created")

    def initialize(self):
        """Initialize and load models based on configuration."""
        logger.info("Initializing models...")

        # Load primary model based on config
        provider = self.config.get('llm.provider', 'local')

        try:
            if provider == 'openai':
                self._load_openai_model()
            elif provider == 'anthropic':
                self._load_anthropic_model()
            elif provider == 'local':
                self._load_local_model()
            else:
                logger.warning(f"Unknown provider: {provider}, using local model")
                self._load_local_model()

            logger.info(f"Model manager initialized with provider: {provider}")

        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            # Fallback to dummy model for development
            self._load_dummy_model()

    def _load_openai_model(self):
        """Load OpenAI model."""
        api_key = self.config.get('llm.openai.api_key')
        model_name = self.config.get('llm.openai.model', 'gpt-4')

        if not api_key:
            logger.warning("OpenAI API key not configured")
            return

        model = OpenAIInterface(
            api_key=api_key,
            model=model_name,
            temperature=self.config.get('llm.openai.temperature', 0.7),
            max_tokens=self.config.get('llm.openai.max_tokens', 4096)
        )

        self.models['openai'] = model
        self.active_model = model
        logger.info(f"Loaded OpenAI model: {model_name}")

    def _load_anthropic_model(self):
        """Load Anthropic model."""
        api_key = self.config.get('llm.anthropic.api_key')
        model_name = self.config.get('llm.anthropic.model', 'claude-3-opus-20240229')

        if not api_key:
            logger.warning("Anthropic API key not configured")
            return

        model = AnthropicInterface(
            api_key=api_key,
            model=model_name,
            temperature=self.config.get('llm.anthropic.temperature', 0.7),
            max_tokens=self.config.get('llm.anthropic.max_tokens', 4096)
        )

        self.models['anthropic'] = model
        self.active_model = model
        logger.info(f"Loaded Anthropic model: {model_name}")

    def _load_local_model(self):
        """Load local model."""
        model_name = self.config.model

        model = LocalModelInterface(
            model_name=model_name,
            model_path=str(self.model_path),
            device=self.config.device
        )

        self.models['local'] = model
        self.active_model = model
        logger.info(f"Loaded local model: {model_name}")

    def _load_dummy_model(self):
        """Load dummy model for testing."""
        from .llm_interface import DummyInterface

        model = DummyInterface()
        self.models['dummy'] = model
        self.active_model = model
        logger.warning("Loaded dummy model (for development/testing)")

    def generate(self, input_data: Any, **kwargs) -> str:
        """
        Generate response using active model.

        Args:
            input_data: Input data (text, dict, etc.)
            **kwargs: Additional generation parameters

        Returns:
            Generated response text
        """
        if not self.active_model:
            raise RuntimeError("No active model loaded")

        # Convert input to text if needed
        if isinstance(input_data, dict):
            # Extract text from structured input
            text = self._extract_text_from_dict(input_data)
        else:
            text = str(input_data)

        # Generate response
        response = self.active_model.generate(text, **kwargs)

        return response

    async def generate_async(self, input_data: Any, **kwargs) -> str:
        """Async version of generate."""
        if not self.active_model:
            raise RuntimeError("No active model loaded")

        text = self._extract_text_from_dict(input_data) if isinstance(input_data, dict) else str(input_data)

        response = await self.active_model.generate_async(text, **kwargs)

        return response

    def _extract_text_from_dict(self, data: Dict[str, Any]) -> str:
        """Extract text from structured data dictionary."""
        # Look for common text fields
        for key in ['text', 'content', 'query', 'input', 'prompt']:
            if key in data:
                return str(data[key])

        # Fallback to JSON representation
        return json.dumps(data)

    def switch_model(self, model_name: str) -> bool:
        """
        Switch active model.

        Args:
            model_name: Name of model to activate

        Returns:
            True if successful, False otherwise
        """
        if model_name in self.models:
            self.active_model = self.models[model_name]
            logger.info(f"Switched to model: {model_name}")
            return True
        else:
            logger.error(f"Model not found: {model_name}")
            return False

    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a model."""
        if model_name is None:
            if self.active_model:
                return self.active_model.get_info()
            else:
                return {'error': 'No active model'}

        if model_name in self.models:
            return self.models[model_name].get_info()
        else:
            return {'error': f'Model not found: {model_name}'}

    def list_models(self) -> List[str]:
        """List all loaded models."""
        return list(self.models.keys())

    def shutdown(self):
        """Shutdown and cleanup models."""
        logger.info("Shutting down model manager...")

        for model_name, model in self.models.items():
            try:
                if hasattr(model, 'shutdown'):
                    model.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down model {model_name}: {e}")

        self.models.clear()
        self.active_model = None

        logger.info("Model manager shutdown complete")

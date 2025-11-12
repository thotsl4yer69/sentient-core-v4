"""
Base plugin interface and types.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins."""
    PERCEPTION = "perception"  # Input processing (sensors, etc.)
    REASONING = "reasoning"  # Inference and logic
    ACTION = "action"  # Output actions
    MEMORY = "memory"  # Memory storage backends
    MODEL = "model"  # LLM interfaces
    INTEGRATION = "integration"  # External integrations
    UTILITY = "utility"  # General utilities


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class Plugin(ABC):
    """
    Base class for all plugins.

    Plugins extend Sentient Core with custom functionality.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin.

        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self.initialized = False
        self.logger = logging.getLogger(f"plugin.{self.metadata.name}")

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        Return plugin metadata.

        Returns:
            PluginMetadata instance
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize plugin.

        Called when plugin is loaded and activated.

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def shutdown(self):
        """
        Shutdown plugin.

        Called when plugin is unloaded.
        Should clean up any resources.
        """
        pass

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration.

        Args:
            config: Configuration dictionary

        Returns:
            True if config is valid
        """
        # Default implementation - override in subclass
        return True

    def get_status(self) -> Dict[str, Any]:
        """
        Get plugin status.

        Returns:
            Status dictionary
        """
        return {
            'name': self.metadata.name,
            'version': self.metadata.version,
            'type': self.metadata.plugin_type.value,
            'initialized': self.initialized,
        }

    def __repr__(self) -> str:
        return f"<Plugin: {self.metadata.name} v{self.metadata.version}>"


class PerceptionPlugin(Plugin):
    """
    Base class for perception plugins.

    Perception plugins process input data (sensors, audio, video, etc.)
    """

    @abstractmethod
    def process(self, data: Any) -> Dict[str, Any]:
        """
        Process input data.

        Args:
            data: Input data to process

        Returns:
            Processed result dictionary
        """
        pass


class ReasoningPlugin(Plugin):
    """
    Base class for reasoning plugins.

    Reasoning plugins implement inference and decision-making logic.
    """

    @abstractmethod
    async def reason(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform reasoning on query.

        Args:
            query: Query or problem to reason about
            context: Additional context information

        Returns:
            Reasoning result
        """
        pass


class ActionPlugin(Plugin):
    """
    Base class for action plugins.

    Action plugins execute actions in response to decisions.
    """

    @abstractmethod
    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.

        Args:
            action: Action name/type
            parameters: Action parameters

        Returns:
            Execution result
        """
        pass


class MemoryPlugin(Plugin):
    """
    Base class for memory plugins.

    Memory plugins implement storage backends for memory systems.
    """

    @abstractmethod
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """
        Store data in memory.

        Args:
            key: Storage key
            value: Data to store
            metadata: Optional metadata
        """
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data from memory.

        Args:
            key: Storage key

        Returns:
            Stored data or None
        """
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Any]:
        """
        Search memory.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching results
        """
        pass


class ModelPlugin(Plugin):
    """
    Base class for model plugins.

    Model plugins provide LLM interfaces.
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            **kwargs: Model-specific parameters

        Returns:
            Generated text
        """
        pass


class IntegrationPlugin(Plugin):
    """
    Base class for integration plugins.

    Integration plugins connect to external services and APIs.
    """

    @abstractmethod
    async def call(self, method: str, parameters: Dict[str, Any]) -> Any:
        """
        Call external service.

        Args:
            method: Method/endpoint name
            parameters: Call parameters

        Returns:
            Response from service
        """
        pass


class UtilityPlugin(Plugin):
    """
    Base class for utility plugins.

    Utility plugins provide helper functions and tools.
    """

    @abstractmethod
    def get_tools(self) -> Dict[str, callable]:
        """
        Get available utility functions.

        Returns:
            Dictionary of tool name to callable
        """
        pass

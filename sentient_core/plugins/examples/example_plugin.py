"""
Example plugin demonstrating plugin system usage.

This is a template for creating custom plugins.
"""

import logging
from typing import Dict, Any

from ..base import UtilityPlugin, PluginMetadata, PluginType

logger = logging.getLogger(__name__)


class ExamplePlugin(UtilityPlugin):
    """
    Example plugin that provides sample utilities.

    This plugin demonstrates:
    - Plugin structure
    - Initialization and shutdown
    - Configuration handling
    - Providing utilities
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize example plugin."""
        super().__init__(config)

        # Plugin-specific attributes
        self.greeting = self.config.get('greeting', 'Hello')
        self.counter = 0

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="example",
            version="1.0.0",
            description="Example plugin demonstrating plugin system usage",
            author="Sentient Core Team",
            plugin_type=PluginType.UTILITY,
            dependencies=[],
            config_schema={
                'greeting': {
                    'type': 'string',
                    'description': 'Greeting message',
                    'default': 'Hello'
                }
            }
        )

    def initialize(self) -> bool:
        """Initialize plugin."""
        try:
            self.logger.info(f"Initializing {self.metadata.name} plugin...")

            # Perform initialization tasks
            self.counter = 0

            self.initialized = True
            self.logger.info(f"{self.metadata.name} plugin initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False

    def shutdown(self):
        """Shutdown plugin."""
        self.logger.info(f"Shutting down {self.metadata.name} plugin...")

        # Cleanup resources
        self.counter = 0

        self.initialized = False
        self.logger.info(f"{self.metadata.name} plugin shutdown complete")

    def get_tools(self) -> Dict[str, callable]:
        """Get available utility functions."""
        return {
            'greet': self.greet,
            'increment': self.increment,
            'get_count': self.get_count,
            'custom_function': self.custom_function,
        }

    def greet(self, name: str = "World") -> str:
        """
        Greet someone.

        Args:
            name: Name to greet

        Returns:
            Greeting message
        """
        message = f"{self.greeting}, {name}!"
        self.logger.debug(f"Greeting: {message}")
        return message

    def increment(self) -> int:
        """
        Increment internal counter.

        Returns:
            New counter value
        """
        self.counter += 1
        return self.counter

    def get_count(self) -> int:
        """
        Get current counter value.

        Returns:
            Counter value
        """
        return self.counter

    def custom_function(self, data: Any) -> Dict[str, Any]:
        """
        Custom processing function.

        Args:
            data: Input data to process

        Returns:
            Processed result
        """
        result = {
            'input': str(data),
            'processed': True,
            'timestamp': self._get_timestamp(),
            'counter': self.counter
        }

        return result

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration.

        Args:
            config: Configuration dictionary

        Returns:
            True if valid
        """
        # Check required fields
        if 'greeting' in config:
            if not isinstance(config['greeting'], str):
                self.logger.error("'greeting' must be a string")
                return False

        return True


# Example perception plugin
from ..base import PerceptionPlugin


class ExampleSensorPlugin(PerceptionPlugin):
    """Example sensor/perception plugin."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="example_sensor",
            version="1.0.0",
            description="Example sensor plugin",
            author="Sentient Core Team",
            plugin_type=PluginType.PERCEPTION
        )

    def initialize(self) -> bool:
        self.logger.info("Example sensor initialized")
        self.initialized = True
        return True

    def shutdown(self):
        self.logger.info("Example sensor shutdown")
        self.initialized = False

    def process(self, data: Any) -> Dict[str, Any]:
        """Process sensor data."""
        return {
            'sensor': 'example',
            'data': data,
            'status': 'processed'
        }

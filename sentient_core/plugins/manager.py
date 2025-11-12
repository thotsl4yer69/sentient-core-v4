"""
Plugin manager for high-level plugin operations.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Type

from .base import Plugin, PluginType
from .loader import PluginLoader
from .registry import PluginRegistry

logger = logging.getLogger(__name__)


class PluginManager:
    """
    High-level plugin management system.

    Coordinates plugin loading, initialization, and lifecycle management.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Components
        self.loader = PluginLoader()
        self.registry = PluginRegistry()

        # Plugin directories
        default_dirs = [
            Path.home() / ".sentient-core" / "plugins",
            Path(__file__).parent.parent.parent / "plugins",  # Project plugins dir
        ]

        for directory in default_dirs:
            if directory.exists():
                self.loader.add_plugin_directory(directory)

        logger.info("Plugin manager initialized")

    def add_plugin_directory(self, directory: Path):
        """
        Add a directory to search for plugins.

        Args:
            directory: Path to plugin directory
        """
        self.loader.add_plugin_directory(directory)

    def discover_plugins(self) -> List[Type[Plugin]]:
        """
        Discover all available plugins.

        Returns:
            List of discovered plugin classes
        """
        return self.loader.discover_plugins()

    def load_plugin(
        self,
        plugin_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Load and initialize a plugin.

        Args:
            plugin_name: Name of plugin to load
            config: Plugin-specific configuration

        Returns:
            True if loaded successfully
        """
        try:
            # Get plugin class
            plugin_class = self.loader.load_plugin_by_name(plugin_name)

            if not plugin_class:
                logger.error(f"Plugin not found: {plugin_name}")
                return False

            # Validate plugin
            if not self.loader.validate_plugin(plugin_class):
                logger.error(f"Plugin validation failed: {plugin_name}")
                return False

            # Check if already loaded
            if self.registry.is_registered(plugin_name):
                logger.warning(f"Plugin {plugin_name} already loaded")
                return True

            # Instantiate plugin
            plugin_config = config or self.config.get(f'plugins.{plugin_name}', {})
            plugin_instance = plugin_class(config=plugin_config)

            # Initialize plugin
            if not plugin_instance.initialize():
                logger.error(f"Plugin initialization failed: {plugin_name}")
                return False

            # Register plugin
            if not self.registry.register(plugin_instance):
                logger.error(f"Plugin registration failed: {plugin_name}")
                plugin_instance.shutdown()
                return False

            logger.info(f"Plugin loaded successfully: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            True if unloaded successfully
        """
        return self.registry.unregister(plugin_name)

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin.

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            True if reloaded successfully
        """
        # Get current config
        plugin = self.registry.get_plugin(plugin_name)
        plugin_config = plugin.config if plugin else {}

        # Unload
        if not self.unload_plugin(plugin_name):
            return False

        # Reload plugin class
        if not self.loader.reload_plugin(plugin_name):
            return False

        # Load again
        return self.load_plugin(plugin_name, config=plugin_config)

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin instance.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.registry.get_plugin(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """
        Get all plugins of a specific type.

        Args:
            plugin_type: Plugin type

        Returns:
            List of plugins
        """
        return self.registry.get_plugins_by_type(plugin_type)

    def load_all_plugins(self, plugin_configs: Optional[Dict[str, Dict]] = None) -> Dict[str, bool]:
        """
        Load all discovered plugins.

        Args:
            plugin_configs: Dictionary of plugin names to configurations

        Returns:
            Dictionary of plugin name to load success status
        """
        plugin_configs = plugin_configs or {}
        results = {}

        # Discover plugins
        plugin_classes = self.discover_plugins()

        # Load each plugin
        for plugin_class in plugin_classes:
            try:
                # Get metadata
                temp_instance = plugin_class(config={})
                plugin_name = temp_instance.metadata.name

                # Load plugin
                config = plugin_configs.get(plugin_name)
                success = self.load_plugin(plugin_name, config)
                results[plugin_name] = success

            except Exception as e:
                logger.error(f"Error loading plugin {plugin_class}: {e}")
                results[str(plugin_class)] = False

        return results

    def unload_all_plugins(self):
        """Unload all plugins."""
        self.registry.clear()

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """
        Get information about a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin info dictionary or None
        """
        return self.registry.get_plugin_info(plugin_name)

    def list_plugins(self) -> List[str]:
        """
        List all loaded plugins.

        Returns:
            List of plugin names
        """
        return list(self.registry.plugins.keys())

    def list_available_plugins(self) -> List[str]:
        """
        List all available (discovered) plugins.

        Returns:
            List of available plugin names
        """
        return list(self.loader.get_loaded_plugins().keys())

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get plugin manager statistics.

        Returns:
            Statistics dictionary
        """
        registry_stats = self.registry.get_statistics()

        stats = {
            'loaded_plugins': registry_stats['total_plugins'],
            'available_plugins': len(self.loader.get_loaded_plugins()),
            'plugins_by_type': registry_stats['by_type'],
            'initialized_plugins': registry_stats['initialized'],
            'plugin_directories': [str(d) for d in self.loader.plugin_dirs],
        }

        return stats

    def call_plugin_method(
        self,
        plugin_name: str,
        method_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Call a method on a plugin.

        Args:
            plugin_name: Name of plugin
            method_name: Name of method to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Method return value

        Raises:
            AttributeError: If plugin or method not found
        """
        plugin = self.get_plugin(plugin_name)

        if not plugin:
            raise AttributeError(f"Plugin not found: {plugin_name}")

        if not hasattr(plugin, method_name):
            raise AttributeError(f"Plugin {plugin_name} has no method: {method_name}")

        method = getattr(plugin, method_name)
        return method(*args, **kwargs)

    def shutdown(self):
        """Shutdown plugin manager and all plugins."""
        logger.info("Shutting down plugin manager...")
        self.unload_all_plugins()
        logger.info("Plugin manager shutdown complete")

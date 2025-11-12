"""
Plugin registry for managing active plugins.
"""

import logging
from typing import Dict, List, Optional
from collections import defaultdict

from .base import Plugin, PluginType

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Central registry for active plugin instances.
    """

    def __init__(self):
        """Initialize plugin registry."""
        self.plugins: Dict[str, Plugin] = {}
        self.plugins_by_type: Dict[PluginType, List[Plugin]] = defaultdict(list)

        logger.info("Plugin registry initialized")

    def register(self, plugin: Plugin) -> bool:
        """
        Register a plugin instance.

        Args:
            plugin: Plugin instance to register

        Returns:
            True if registered successfully
        """
        try:
            plugin_name = plugin.metadata.name

            if plugin_name in self.plugins:
                logger.warning(f"Plugin {plugin_name} already registered, replacing...")
                self.unregister(plugin_name)

            # Register
            self.plugins[plugin_name] = plugin
            self.plugins_by_type[plugin.metadata.plugin_type].append(plugin)

            logger.info(f"Registered plugin: {plugin_name} ({plugin.metadata.plugin_type.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False

    def unregister(self, plugin_name: str) -> bool:
        """
        Unregister a plugin.

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if unregistered successfully
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin {plugin_name} not registered")
            return False

        try:
            plugin = self.plugins[plugin_name]

            # Shutdown plugin
            if plugin.initialized:
                plugin.shutdown()

            # Remove from registry
            del self.plugins[plugin_name]

            # Remove from type index
            self.plugins_by_type[plugin.metadata.plugin_type].remove(plugin)

            logger.info(f"Unregistered plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister plugin {plugin_name}: {e}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """
        Get all plugins of a specific type.

        Args:
            plugin_type: Plugin type

        Returns:
            List of plugins
        """
        return self.plugins_by_type.get(plugin_type, []).copy()

    def get_all_plugins(self) -> List[Plugin]:
        """
        Get all registered plugins.

        Returns:
            List of all plugins
        """
        return list(self.plugins.values())

    def is_registered(self, plugin_name: str) -> bool:
        """
        Check if a plugin is registered.

        Args:
            plugin_name: Plugin name

        Returns:
            True if registered
        """
        return plugin_name in self.plugins

    def get_plugin_count(self) -> int:
        """
        Get total number of registered plugins.

        Returns:
            Plugin count
        """
        return len(self.plugins)

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """
        Get information about a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin info dictionary or None
        """
        plugin = self.get_plugin(plugin_name)

        if plugin:
            return {
                'name': plugin.metadata.name,
                'version': plugin.metadata.version,
                'description': plugin.metadata.description,
                'author': plugin.metadata.author,
                'type': plugin.metadata.plugin_type.value,
                'initialized': plugin.initialized,
                'dependencies': plugin.metadata.dependencies,
            }

        return None

    def get_all_plugin_info(self) -> List[Dict]:
        """
        Get information about all registered plugins.

        Returns:
            List of plugin info dictionaries
        """
        return [
            self.get_plugin_info(name)
            for name in self.plugins.keys()
        ]

    def clear(self):
        """Unregister all plugins."""
        plugin_names = list(self.plugins.keys())

        for name in plugin_names:
            self.unregister(name)

        self.plugins.clear()
        self.plugins_by_type.clear()

        logger.info("Registry cleared")

    def get_statistics(self) -> Dict:
        """
        Get registry statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            'total_plugins': len(self.plugins),
            'by_type': {},
            'initialized': 0,
        }

        for plugin_type in PluginType:
            count = len(self.plugins_by_type.get(plugin_type, []))
            stats['by_type'][plugin_type.value] = count

        stats['initialized'] = sum(
            1 for p in self.plugins.values()
            if p.initialized
        )

        return stats

"""
Plugin loader for discovering and loading plugins.
"""

import logging
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import List, Optional, Type, Dict

from .base import Plugin

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Discovers and loads plugins from various sources.
    """

    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """
        Initialize plugin loader.

        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or []
        self.loaded_plugins: Dict[str, Type[Plugin]] = {}

        logger.info(f"Plugin loader initialized with {len(self.plugin_dirs)} search paths")

    def add_plugin_directory(self, directory: Path):
        """
        Add a directory to search for plugins.

        Args:
            directory: Path to plugin directory
        """
        directory = Path(directory)
        if directory.exists() and directory.is_dir():
            self.plugin_dirs.append(directory)
            logger.info(f"Added plugin directory: {directory}")
        else:
            logger.warning(f"Plugin directory does not exist: {directory}")

    def discover_plugins(self) -> List[Type[Plugin]]:
        """
        Discover all available plugins.

        Returns:
            List of plugin classes
        """
        discovered = []

        for plugin_dir in self.plugin_dirs:
            logger.info(f"Searching for plugins in: {plugin_dir}")

            # Find all Python files
            for py_file in plugin_dir.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                try:
                    plugin_classes = self._load_plugin_from_file(py_file)
                    discovered.extend(plugin_classes)

                except Exception as e:
                    logger.error(f"Failed to load plugin from {py_file}: {e}")

        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered

    def _load_plugin_from_file(self, file_path: Path) -> List[Type[Plugin]]:
        """
        Load plugin classes from a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            List of plugin classes found
        """
        plugins = []

        try:
            # Import module from file
            spec = importlib.util.spec_from_file_location(
                file_path.stem,
                file_path
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find Plugin subclasses
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                        issubclass(obj, Plugin) and
                        obj is not Plugin):  # Skip base Plugin class

                        plugins.append(obj)
                        plugin_key = getattr(getattr(obj, 'metadata', None), 'name', name)
                        self.loaded_plugins[plugin_key] = obj
                        logger.debug(f"Loaded plugin class: {name} from {file_path}")

        except Exception as e:
            logger.error(f"Error loading plugin from {file_path}: {e}")
            raise

        return plugins

    def load_plugin_by_name(self, plugin_name: str) -> Optional[Type[Plugin]]:
        """
        Load a specific plugin by name.

        Args:
            plugin_name: Name of plugin to load

        Returns:
            Plugin class or None
        """
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]

        # Try to discover if not already loaded
        self.discover_plugins()

        return self.loaded_plugins.get(plugin_name)

    def load_plugin_from_module(self, module_path: str) -> Optional[Type[Plugin]]:
        """
        Load plugin from a Python module path.

        Args:
            module_path: Python module path (e.g., 'mypackage.myplugin')

        Returns:
            Plugin class or None
        """
        try:
            module = importlib.import_module(module_path)

            # Find Plugin subclass
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, Plugin) and
                    obj is not Plugin):

                    self.loaded_plugins[name] = obj
                    logger.info(f"Loaded plugin from module: {module_path}")
                    return obj

            logger.warning(f"No Plugin class found in module: {module_path}")
            return None

        except ImportError as e:
            logger.error(f"Failed to import plugin module {module_path}: {e}")
            return None

    def get_loaded_plugins(self) -> Dict[str, Type[Plugin]]:
        """
        Get all loaded plugin classes.

        Returns:
            Dictionary of plugin name to class
        """
        return self.loaded_plugins.copy()

    def validate_plugin(self, plugin_class: Type[Plugin]) -> bool:
        """
        Validate a plugin class.

        Args:
            plugin_class: Plugin class to validate

        Returns:
            True if valid
        """
        try:
            # Check if it's a proper subclass
            if not issubclass(plugin_class, Plugin):
                logger.error(f"{plugin_class} is not a Plugin subclass")
                return False

            # Check required methods
            required_methods = ['initialize', 'shutdown', 'metadata']

            for method in required_methods:
                if not hasattr(plugin_class, method):
                    logger.error(f"Plugin {plugin_class} missing required method: {method}")
                    return False

            # Try to instantiate (with empty config)
            try:
                instance = plugin_class(config={})
                if not hasattr(instance, 'metadata'):
                    logger.error(f"Plugin {plugin_class} has no metadata")
                    return False
            except Exception as e:
                logger.error(f"Failed to instantiate plugin {plugin_class}: {e}")
                return False

            return True

        except Exception as e:
            logger.error(f"Plugin validation error: {e}")
            return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin.

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            True if successful
        """
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"Plugin {plugin_name} not loaded")
            return False

        try:
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]

            # Rediscover
            self.discover_plugins()

            return plugin_name in self.loaded_plugins

        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False

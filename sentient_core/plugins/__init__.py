"""
Sentient Core Plugin System

Extensible plugin architecture for adding custom functionality.
"""

from .base import Plugin, PluginMetadata, PluginType
from .loader import PluginLoader
from .registry import PluginRegistry
from .manager import PluginManager

__all__ = [
    'Plugin',
    'PluginMetadata',
    'PluginType',
    'PluginLoader',
    'PluginRegistry',
    'PluginManager',
]

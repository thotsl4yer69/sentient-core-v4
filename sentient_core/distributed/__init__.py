"""
Distributed Consciousness System for Sentient Core v4.

Enables multi-node AI coordination across edge devices (Pi 5, Jetson, etc.)
with synchronized state and intelligent task routing.
"""

from .consciousness import DistributedConsciousness
from .node import Node, NodeRole, NodeCapability
from .sync_manager import SyncManager
from .cortana_unified import CortanaUnified

__all__ = [
    "DistributedConsciousness",
    "Node",
    "NodeRole",
    "NodeCapability",
    "SyncManager",
    "CortanaUnified",
]

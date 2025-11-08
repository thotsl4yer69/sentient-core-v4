"""
Hardware abstraction layer for Sentient Core v4.

Provides unified interfaces for various AI accelerators and edge hardware:
- Hailo AI Hat (Pi 5)
- Google Coral TPU
- NVIDIA Jetson
- CPU/GPU fallbacks
"""

from .base import HardwareInterface, HardwareType
from .hailo_interface import HailoInterface
from .coral_interface import CoralInterface
from .hardware_manager import HardwareManager

__all__ = [
    "HardwareInterface",
    "HardwareType",
    "HailoInterface",
    "CoralInterface",
    "HardwareManager",
]

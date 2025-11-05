"""
Sentient Core v4 - Advanced AI Cognitive Architecture

A next-generation artificial intelligence framework for building autonomous,
self-aware cognitive systems with advanced reasoning capabilities.
"""

__version__ = "4.0.0"
__author__ = "Sentient Core Team"
__license__ = "MIT"

from .core.agent import SentientAgent
from .agents.base_agent import BaseAgent
from .agents.team import AgentTeam
from .models.model_manager import ModelManager
from .voice.voice_processor import VoiceProcessor
from .pixelscape.vision_system import VisionSystem

__all__ = [
    "SentientAgent",
    "BaseAgent",
    "AgentTeam",
    "ModelManager",
    "VoiceProcessor",
    "VisionSystem",
]

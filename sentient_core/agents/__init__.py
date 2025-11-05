"""
Multi-agent system for coordination and collaboration.
"""

from .base_agent import BaseAgent
from .team import AgentTeam
from .specialized_agents import (
    ResearchAgent,
    AnalysisAgent,
    ExecutionAgent,
    CoordinatorAgent
)

__all__ = [
    "BaseAgent",
    "AgentTeam",
    "ResearchAgent",
    "AnalysisAgent",
    "ExecutionAgent",
    "CoordinatorAgent",
]

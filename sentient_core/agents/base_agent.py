"""
Base agent class for all specialized agents.
"""

import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import uuid


logger = logging.getLogger(__name__)


@dataclass
class AgentCapability:
    """Defines an agent capability."""
    name: str
    description: str
    enabled: bool = True


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.

    Each agent has specific capabilities and can collaborate with other agents
    through the AgentTeam coordinator.
    """

    def __init__(self, agent_id: Optional[str] = None, name: Optional[str] = None):
        """
        Initialize base agent.

        Args:
            agent_id: Unique agent identifier
            name: Human-readable agent name
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or f"Agent-{self.agent_id[:8]}"
        self.capabilities: List[AgentCapability] = []
        self.state: Dict[str, Any] = {}
        self.memory: List[Dict[str, Any]] = []
        self.active = False

        logger.info(f"Agent initialized: {self.name} ({self.agent_id})")

    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of agent capabilities."""
        pass

    @abstractmethod
    def process_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a task assigned to this agent.

        Args:
            task: Task description
            context: Optional context information

        Returns:
            Task result dictionary
        """
        pass

    def activate(self):
        """Activate the agent."""
        self.active = True
        logger.info(f"Agent activated: {self.name}")

    def deactivate(self):
        """Deactivate the agent."""
        self.active = False
        logger.info(f"Agent deactivated: {self.name}")

    def add_to_memory(self, entry: Dict[str, Any]):
        """Add an entry to agent's memory."""
        self.memory.append(entry)

    def get_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent memory entries."""
        return self.memory[-limit:]

    def update_state(self, key: str, value: Any):
        """Update agent state."""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get agent state value."""
        return self.state.get(key, default)

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'active': self.active,
            'capabilities': [
                {'name': cap.name, 'description': cap.description}
                for cap in self.capabilities
            ],
            'memory_size': len(self.memory),
            'state': self.state
        }

    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type."""
        return any(cap.name == task_type and cap.enabled for cap in self.capabilities)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id[:8]}, name={self.name}, active={self.active})>"

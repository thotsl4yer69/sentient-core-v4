"""
Node definitions for distributed consciousness network.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class NodeRole(Enum):
    """Role of a node in the distributed system."""
    FAST_RESPONSE = "fast_response"      # Quick responses, low latency
    DEEP_REASONING = "deep_reasoning"    # Complex reasoning, multimodal
    COORDINATOR = "coordinator"          # Orchestrates other nodes
    WORKER = "worker"                    # General-purpose worker
    EDGE = "edge"                        # Edge device with sensors


class NodeCapability(Enum):
    """Capabilities that a node can provide."""
    TEXT_GENERATION = "text_generation"
    VISION_ANALYSIS = "vision_analysis"
    AUDIO_PROCESSING = "audio_processing"
    RF_MONITORING = "rf_monitoring"
    SENSOR_FUSION = "sensor_fusion"
    FAST_INFERENCE = "fast_inference"
    MULTIMODAL = "multimodal"
    VECTOR_SEARCH = "vector_search"
    REASONING = "reasoning"
    MEMORY_STORAGE = "memory_storage"


@dataclass
class NodeSpec:
    """Specification for a distributed node."""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "unnamed_node"
    role: NodeRole = NodeRole.WORKER
    capabilities: List[NodeCapability] = field(default_factory=list)
    endpoint_url: Optional[str] = None
    hardware: str = "unknown"
    model: Optional[str] = None
    max_latency: float = 5.0  # seconds
    priority: int = 1  # Higher = more priority for task routing


@dataclass
class Node:
    """
    Represents a node in the distributed consciousness network.

    Each node can be a different device (Pi 5, Jetson, cloud instance)
    with specific capabilities and hardware.
    """
    spec: NodeSpec
    status: str = "offline"
    last_seen: Optional[datetime] = None
    active_tasks: int = 0
    total_requests: int = 0
    average_latency: float = 0.0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize node after dataclass creation."""
        if self.last_seen is None:
            self.last_seen = datetime.now()

    @property
    def is_online(self) -> bool:
        """Check if node is online based on last_seen."""
        if not self.last_seen:
            return False

        # Consider offline if not seen in last 30 seconds
        delta = (datetime.now() - self.last_seen).total_seconds()
        return delta < 30 and self.status == "online"

    @property
    def health_score(self) -> float:
        """
        Calculate node health score (0.0 to 1.0).

        Based on:
        - Online status
        - Error rate
        - Latency
        """
        if not self.is_online:
            return 0.0

        # Base score for being online
        score = 0.5

        # Penalize for errors
        if self.total_requests > 0:
            error_rate = self.error_count / self.total_requests
            score -= (error_rate * 0.3)

        # Penalize for high latency
        if self.average_latency > self.spec.max_latency:
            latency_penalty = min(0.2, (self.average_latency - self.spec.max_latency) / 10)
            score -= latency_penalty
        else:
            # Bonus for good latency
            score += 0.2

        # Penalize for high load
        if self.active_tasks > 5:
            load_penalty = min(0.2, (self.active_tasks - 5) / 20)
            score -= load_penalty

        return max(0.0, min(1.0, score))

    def can_handle(self, required_capability: NodeCapability) -> bool:
        """Check if node has required capability."""
        return required_capability in self.spec.capabilities and self.is_online

    def update_latency(self, new_latency: float):
        """Update running average of latency."""
        if self.total_requests == 0:
            self.average_latency = new_latency
        else:
            # Exponential moving average
            alpha = 0.3
            self.average_latency = alpha * new_latency + (1 - alpha) * self.average_latency

    def record_request(self, success: bool = True, latency: Optional[float] = None):
        """Record a request to this node."""
        self.total_requests += 1
        if not success:
            self.error_count += 1
        if latency is not None:
            self.update_latency(latency)
        self.last_seen = datetime.now()

    def heartbeat(self):
        """Update node heartbeat."""
        self.last_seen = datetime.now()
        if self.status != "online":
            self.status = "online"

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            'node_id': self.spec.node_id,
            'name': self.spec.name,
            'role': self.spec.role.value,
            'capabilities': [cap.value for cap in self.spec.capabilities],
            'endpoint_url': self.spec.endpoint_url,
            'hardware': self.spec.hardware,
            'model': self.spec.model,
            'status': self.status,
            'is_online': self.is_online,
            'health_score': self.health_score,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'active_tasks': self.active_tasks,
            'total_requests': self.total_requests,
            'average_latency': self.average_latency,
            'error_count': self.error_count,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """Create node from dictionary representation."""
        spec = NodeSpec(
            node_id=data['node_id'],
            name=data['name'],
            role=NodeRole(data['role']),
            capabilities=[NodeCapability(cap) for cap in data.get('capabilities', [])],
            endpoint_url=data.get('endpoint_url'),
            hardware=data.get('hardware', 'unknown'),
            model=data.get('model'),
            max_latency=data.get('max_latency', 5.0),
            priority=data.get('priority', 1)
        )

        node = cls(
            spec=spec,
            status=data.get('status', 'offline'),
            active_tasks=data.get('active_tasks', 0),
            total_requests=data.get('total_requests', 0),
            average_latency=data.get('average_latency', 0.0),
            error_count=data.get('error_count', 0),
            metadata=data.get('metadata', {})
        )

        if 'last_seen' in data and data['last_seen']:
            node.last_seen = datetime.fromisoformat(data['last_seen'])

        return node

    def __repr__(self) -> str:
        return f"<Node(id={self.spec.node_id[:8]}, name={self.spec.name}, role={self.spec.role.value}, online={self.is_online})>"

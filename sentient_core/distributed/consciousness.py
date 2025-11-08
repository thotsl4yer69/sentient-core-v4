"""
Distributed Consciousness - Multi-Node AI Coordination System.

Synchronizes multiple AI nodes into a unified consciousness across
Raspberry Pi 5, Jetson Orin, and other edge devices.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .node import Node, NodeSpec, NodeRole, NodeCapability
from .sync_manager import SyncManager

logger = logging.getLogger(__name__)


class DistributedConsciousness:
    """
    Coordinates multiple AI nodes into unified consciousness.

    Manages node registration, state synchronization, and intelligent
    task routing based on node capabilities and load.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize distributed consciousness.

        Args:
            config: Configuration object
        """
        self.config = config or {}
        self.nodes: Dict[str, Node] = {}
        self.local_node: Optional[Node] = None
        self.sync_manager: Optional[SyncManager] = None

        # Shared consciousness state
        self.shared_state = {
            'conversation_history': [],
            'user_context': {},
            'active_tasks': [],
            'world_model': {},
            'emotional_state': 'focused',
            'last_sync': None
        }

        self.running = False
        self.sync_interval = 0.1  # 10Hz sync rate

        # Background tasks
        self.sync_task: Optional[asyncio.Task] = None
        self.discovery_task: Optional[asyncio.Task] = None

        logger.info("Distributed Consciousness initialized")

    async def start(self, local_node_spec: NodeSpec):
        """
        Start distributed consciousness system.

        Args:
            local_node_spec: Specification for the local node
        """
        self.running = True

        # Create local node
        self.local_node = Node(
            spec=local_node_spec,
            status="online",
            last_seen=datetime.now()
        )

        logger.info(f"Local node initialized: {self.local_node.spec.name} ({self.local_node.spec.role.value})")

        # Initialize sync manager
        self.sync_manager = SyncManager(self.shared_state)

        # Start sync loop
        self.sync_task = asyncio.create_task(self._sync_loop())

        # Start node discovery (if configured)
        if self.config.get('enable_discovery', False):
            self.discovery_task = asyncio.create_task(self._discovery_loop())

        logger.info("Distributed Consciousness operational")

    async def register_remote_node(self, node_spec: NodeSpec) -> bool:
        """
        Register a remote node.

        Args:
            node_spec: Specification of remote node

        Returns:
            True if successful
        """
        try:
            # Create node object
            node = Node(
                spec=node_spec,
                status="offline",
                last_seen=None
            )

            # Attempt to contact node
            if node_spec.endpoint_url:
                success = await self._ping_node(node)
                if success:
                    node.status = "online"
                    node.last_seen = datetime.now()

            self.nodes[node_spec.node_id] = node
            logger.info(f"Registered remote node: {node_spec.name} at {node_spec.endpoint_url}")

            return True

        except Exception as e:
            logger.error(f"Failed to register node {node_spec.name}: {e}")
            return False

    async def _ping_node(self, node: Node) -> bool:
        """Ping a remote node to check availability."""
        if not node.spec.endpoint_url:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{node.spec.endpoint_url}/health"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        node.heartbeat()
                        return True
                    return False

        except Exception as e:
            logger.debug(f"Ping failed for {node.spec.name}: {e}")
            return False

    async def _sync_loop(self):
        """Continuous state synchronization loop."""
        while self.running:
            try:
                # Broadcast state to remote nodes
                await self._broadcast_state()

                # Check health of remote nodes
                await self._check_node_health()

                # Update shared state
                self.shared_state['last_sync'] = datetime.now().isoformat()

                await asyncio.sleep(self.sync_interval)

            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                await asyncio.sleep(1)

    async def _broadcast_state(self):
        """Broadcast local state to all remote nodes."""
        if not self.local_node:
            return

        state_update = {
            'node_id': self.local_node.spec.node_id,
            'state': self.shared_state,
            'timestamp': datetime.now().isoformat()
        }

        for node_id, node in self.nodes.items():
            if not node.is_online or not node.spec.endpoint_url:
                continue

            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{node.spec.endpoint_url}/sync"
                    async with session.post(
                        url,
                        json=state_update,
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as resp:
                        if resp.status == 200:
                            node.heartbeat()
                        else:
                            logger.debug(f"Sync failed for {node.spec.name}: HTTP {resp.status}")

            except asyncio.TimeoutError:
                logger.debug(f"Sync timeout for {node.spec.name}")
            except Exception as e:
                logger.debug(f"Sync error for {node.spec.name}: {e}")

    async def _check_node_health(self):
        """Check health of all remote nodes."""
        for node in self.nodes.values():
            if node.spec.endpoint_url:
                await self._ping_node(node)

    async def _discovery_loop(self):
        """Auto-discovery of nodes on local network."""
        while self.running:
            try:
                # TODO: Implement mDNS/Bonjour discovery
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Discovery error: {e}")
                await asyncio.sleep(60)

    async def route_query(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        required_capability: Optional[NodeCapability] = None
    ) -> Dict[str, Any]:
        """
        Intelligently route query to best available node.

        Args:
            user_input: User's input text
            context: Optional context dictionary
            required_capability: Specific capability required (optional)

        Returns:
            Response dictionary
        """
        # Assess query complexity
        complexity = self._assess_complexity(user_input, required_capability)

        # Find best node for task
        target_node = self._select_node(complexity, required_capability)

        if not target_node:
            logger.warning("No suitable node found for query")
            return {
                'error': 'No suitable node available',
                'text': 'System temporarily unavailable'
            }

        # Execute on target node
        if target_node == self.local_node:
            return await self._local_inference(user_input, context)
        else:
            return await self._remote_inference(user_input, context, target_node)

    def _assess_complexity(
        self,
        query: str,
        required_capability: Optional[NodeCapability] = None
    ) -> str:
        """
        Assess query complexity for routing.

        Returns:
            'simple', 'moderate', 'complex', or 'vision'
        """
        if required_capability == NodeCapability.VISION_ANALYSIS:
            return 'vision'

        query_lower = query.lower()

        # Keywords indicating complexity
        simple_keywords = ['status', 'hello', 'hi', 'thanks', 'ok', 'yes', 'no']
        complex_keywords = ['analyze', 'explain', 'compare', 'calculate', 'design', 'reason']
        vision_keywords = ['see', 'look', 'image', 'show', 'picture', 'detect']

        if any(kw in query_lower for kw in vision_keywords):
            return 'vision'
        elif any(kw in query_lower for kw in complex_keywords):
            return 'complex'
        elif any(kw in query_lower for kw in simple_keywords) or len(query.split()) < 5:
            return 'simple'
        else:
            return 'moderate'

    def _select_node(
        self,
        complexity: str,
        required_capability: Optional[NodeCapability] = None
    ) -> Optional[Node]:
        """
        Select best node for task based on complexity and capabilities.

        Args:
            complexity: Query complexity level
            required_capability: Required capability (if any)

        Returns:
            Selected node or None
        """
        # Filter nodes by capability if specified
        if required_capability:
            candidates = [
                node for node in self._all_nodes()
                if node.can_handle(required_capability)
            ]
        else:
            candidates = [node for node in self._all_nodes() if node.is_online]

        if not candidates:
            return None

        # Route based on complexity
        if complexity == 'simple':
            # Prefer fast response nodes
            fast_nodes = [n for n in candidates if n.spec.role == NodeRole.FAST_RESPONSE]
            if fast_nodes:
                return self._best_node(fast_nodes)

        elif complexity in ['complex', 'vision']:
            # Prefer deep reasoning or multimodal nodes
            deep_nodes = [
                n for n in candidates
                if n.spec.role == NodeRole.DEEP_REASONING or
                   NodeCapability.MULTIMODAL in n.spec.capabilities
            ]
            if deep_nodes:
                return self._best_node(deep_nodes)

        # Default: select best available node
        return self._best_node(candidates)

    def _best_node(self, candidates: List[Node]) -> Optional[Node]:
        """
        Select best node from candidates based on health and load.

        Args:
            candidates: List of candidate nodes

        Returns:
            Best node or None
        """
        if not candidates:
            return None

        # Score nodes
        scored_nodes = []
        for node in candidates:
            score = node.health_score

            # Bonus for local node (no network latency)
            if node == self.local_node:
                score += 0.2

            # Factor in priority
            score *= (node.spec.priority / 5.0)

            scored_nodes.append((score, node))

        # Sort by score (descending)
        scored_nodes.sort(reverse=True, key=lambda x: x[0])

        return scored_nodes[0][1]

    def _all_nodes(self) -> List[Node]:
        """Get all nodes including local node."""
        nodes = list(self.nodes.values())
        if self.local_node:
            nodes.append(self.local_node)
        return nodes

    async def _local_inference(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run inference on local node.

        Args:
            user_input: User input
            context: Optional context

        Returns:
            Response dictionary
        """
        # This will be implemented by the local agent
        return {
            'text': f"Local processing: {user_input[:50]}...",
            'node': self.local_node.spec.node_id if self.local_node else 'unknown',
            'latency': 0.5,
            'confidence': 0.85
        }

    async def _remote_inference(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        target_node: Optional[Node] = None
    ) -> Dict[str, Any]:
        """
        Run inference on remote node.

        Args:
            user_input: User input
            context: Optional context
            target_node: Target node for inference

        Returns:
            Response dictionary
        """
        if not target_node or not target_node.spec.endpoint_url:
            raise ValueError("Invalid target node")

        start_time = datetime.now()

        try:
            target_node.active_tasks += 1

            async with aiohttp.ClientSession() as session:
                url = f"{target_node.spec.endpoint_url}/inference"
                payload = {
                    'input': user_input,
                    'context': context or {},
                    'timestamp': datetime.now().isoformat()
                }

                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=target_node.spec.max_latency)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        latency = (datetime.now() - start_time).total_seconds()
                        target_node.record_request(success=True, latency=latency)
                        return result
                    else:
                        error_text = await resp.text()
                        logger.error(f"Remote inference failed: HTTP {resp.status} - {error_text}")
                        target_node.record_request(success=False)
                        return await self._local_inference(user_input, context)

        except asyncio.TimeoutError:
            logger.error(f"Remote inference timeout for {target_node.spec.name}")
            target_node.record_request(success=False)
            return await self._local_inference(user_input, context)

        except Exception as e:
            logger.error(f"Remote inference error: {e}")
            target_node.record_request(success=False)
            return await self._local_inference(user_input, context)

        finally:
            target_node.active_tasks = max(0, target_node.active_tasks - 1)

    async def update_shared_state(self, key: str, value: Any):
        """Update shared consciousness state."""
        self.shared_state[key] = value
        self.shared_state['last_update'] = datetime.now().isoformat()

    def get_shared_state(self) -> Dict[str, Any]:
        """Get current shared state."""
        return self.shared_state.copy()

    def get_all_nodes_info(self) -> List[Dict[str, Any]]:
        """Get information about all nodes."""
        return [node.to_dict() for node in self._all_nodes()]

    async def stop(self):
        """Stop distributed consciousness."""
        self.running = False

        # Cancel background tasks
        if self.sync_task and not self.sync_task.done():
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                # Task cancellation is expected during shutdown; safe to ignore.

        if self.discovery_task and not self.discovery_task.done():
            self.discovery_task.cancel()
            try:
                await self.discovery_task
            except asyncio.CancelledError:
                # Task cancellation is expected during shutdown; safe to ignore.

        logger.info("Distributed Consciousness stopped")

    def __repr__(self) -> str:
        node_count = len(self.nodes) + (1 if self.local_node else 0)
        return f"<DistributedConsciousness(nodes={node_count}, running={self.running})>"

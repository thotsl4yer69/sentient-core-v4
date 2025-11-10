"""
Heartbeat monitoring for distributed nodes.

Implements ping/pong heartbeat to detect crashed or unresponsive nodes.
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HeartbeatMonitor:
    """
    Monitors node health via ping/pong heartbeats.

    Detects crashed or unresponsive nodes that don't respond to pings.
    """

    def __init__(self, ping_interval: float = 5.0, timeout: float = 15.0):
        """
        Initialize heartbeat monitor.

        Args:
            ping_interval: Seconds between ping attempts
            timeout: Seconds before declaring node dead
        """
        self.ping_interval = ping_interval
        self.timeout = timeout

        # Track last pong from each node
        self.last_pong: Dict[str, datetime] = {}

        # Track if nodes are alive
        self.alive_nodes: Dict[str, bool] = {}

        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None

        logger.info(f"Heartbeat monitor initialized (interval={ping_interval}s, timeout={timeout}s)")

    async def start(self, nodes: Dict[str, Any], ping_callback, status_callback):
        """
        Start heartbeat monitoring.

        Args:
            nodes: Dictionary of nodes to monitor
            ping_callback: Async function to call to ping a node (node_id) -> None
            status_callback: Async function to call when node status changes (node_id, is_alive) -> None
        """
        self.running = True
        self.ping_callback = ping_callback
        self.status_callback = status_callback

        # Initialize all nodes as alive
        for node_id in nodes.keys():
            self.alive_nodes[node_id] = True
            self.last_pong[node_id] = datetime.now()

        # Start monitoring loop
        self.monitor_task = asyncio.create_task(self._monitor_loop(nodes))

        logger.info("Heartbeat monitoring started")

    async def _monitor_loop(self, nodes: Dict[str, Any]):
        """Main monitoring loop."""
        while self.running:
            try:
                # Send ping to all nodes
                for node_id in nodes.keys():
                    try:
                        await self.ping_callback(node_id)
                    except Exception as e:
                        logger.error(f"Failed to ping {node_id}: {e}")

                # Check for timeouts
                now = datetime.now()
                for node_id, last_pong_time in self.last_pong.items():
                    time_since_pong = (now - last_pong_time).total_seconds()

                    was_alive = self.alive_nodes.get(node_id, True)
                    is_alive = time_since_pong < self.timeout

                    # Status changed
                    if was_alive != is_alive:
                        self.alive_nodes[node_id] = is_alive

                        if is_alive:
                            logger.info(f"✓ Node {node_id} came back online")
                        else:
                            logger.error(f"✗ Node {node_id} is unresponsive (no pong for {time_since_pong:.1f}s)")

                        # Notify status change
                        try:
                            await self.status_callback(node_id, is_alive)
                        except Exception as e:
                            logger.error(f"Status callback failed: {e}")

                # Wait for next ping interval
                await asyncio.sleep(self.ping_interval)

            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                await asyncio.sleep(self.ping_interval)

    def record_pong(self, node_id: str):
        """
        Record pong response from node.

        Args:
            node_id: ID of node that ponged
        """
        self.last_pong[node_id] = datetime.now()

        # If node was dead, mark as alive
        if not self.alive_nodes.get(node_id, True):
            logger.info(f"✓ Node {node_id} responded to ping (recovered)")
            self.alive_nodes[node_id] = True

    def is_alive(self, node_id: str) -> bool:
        """
        Check if node is alive.

        Args:
            node_id: Node to check

        Returns:
            True if alive
        """
        return self.alive_nodes.get(node_id, False)

    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all monitored nodes.

        Returns:
            Dictionary with node status
        """
        now = datetime.now()
        status = {}

        for node_id, last_pong_time in self.last_pong.items():
            time_since_pong = (now - last_pong_time).total_seconds()

            status[node_id] = {
                'alive': self.alive_nodes.get(node_id, False),
                'last_pong': last_pong_time.isoformat(),
                'seconds_since_pong': time_since_pong,
                'status': 'online' if self.is_alive(node_id) else 'offline'
            }

        return status

    async def stop(self):
        """Stop heartbeat monitoring."""
        self.running = False

        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("Heartbeat monitoring stopped")

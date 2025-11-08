"""
Synchronization Manager for distributed state management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import json

logger = logging.getLogger(__name__)


class SyncManager:
    """
    Manages state synchronization across distributed nodes.

    Ensures eventual consistency of shared consciousness state.
    """

    def __init__(self, shared_state: Dict[str, Any]):
        """
        Initialize sync manager.

        Args:
            shared_state: Reference to shared state dictionary
        """
        self.shared_state = shared_state
        self.version_vector: Dict[str, int] = {}
        self.pending_updates: List[Dict[str, Any]] = []
        self.sync_lock = asyncio.Lock()

    def compute_state_hash(self) -> str:
        """
        Compute hash of current state.

        Returns:
            SHA-256 hash of state
        """
        state_json = json.dumps(self.shared_state, sort_keys=True, default=str)
        return hashlib.sha256(state_json.encode()).hexdigest()

    async def merge_state(self, remote_state: Dict[str, Any], node_id: str):
        """
        Merge remote state with local state.

        Args:
            remote_state: State from remote node
            node_id: ID of remote node
        """
        async with self.sync_lock:
            try:
                # Merge conversation history
                if 'conversation_history' in remote_state:
                    self._merge_list(
                        'conversation_history',
                        remote_state['conversation_history']
                    )

                # Merge world model
                if 'world_model' in remote_state:
                    self._merge_dict(
                        'world_model',
                        remote_state['world_model']
                    )

                # Merge active tasks
                if 'active_tasks' in remote_state:
                    self._merge_list(
                        'active_tasks',
                        remote_state['active_tasks']
                    )

                # Update user context (latest wins)
                if 'user_context' in remote_state:
                    self.shared_state['user_context'].update(
                        remote_state['user_context']
                    )

                # Increment version
                self.version_vector[node_id] = self.version_vector.get(node_id, 0) + 1

                logger.debug(f"Merged state from {node_id}")

            except Exception as e:
                logger.error(f"State merge error: {e}")

    def _merge_list(self, key: str, remote_list: List[Any]):
        """
        Merge remote list with local list.

        Deduplicates and maintains order.
        """
        if key not in self.shared_state:
            self.shared_state[key] = []

        local_list = self.shared_state[key]

        # Add items not already present
        for item in remote_list:
            if item not in local_list:
                local_list.append(item)

        # Limit size to prevent unbounded growth
        max_size = 100
        if len(local_list) > max_size:
            self.shared_state[key] = local_list[-max_size:]

    def _merge_dict(self, key: str, remote_dict: Dict[str, Any]):
        """
        Merge remote dictionary with local dictionary.

        Uses timestamp-based last-write-wins for conflicts.
        """
        if key not in self.shared_state:
            self.shared_state[key] = {}

        self.shared_state[key].update(remote_dict)

    async def get_sync_package(self) -> Dict[str, Any]:
        """
        Create synchronization package to send to other nodes.

        Returns:
            Dictionary with state and metadata
        """
        async with self.sync_lock:
            return {
                'state': self.shared_state.copy(),
                'version_vector': self.version_vector.copy(),
                'state_hash': self.compute_state_hash(),
                'timestamp': datetime.now().isoformat()
            }

    async def apply_sync_package(self, package: Dict[str, Any], node_id: str) -> bool:
        """
        Apply synchronization package from remote node.

        Args:
            package: Sync package from remote node
            node_id: ID of sending node

        Returns:
            True if successfully applied
        """
        try:
            if 'state' in package:
                await self.merge_state(package['state'], node_id)

            if 'version_vector' in package:
                # Update version vector
                for nid, version in package['version_vector'].items():
                    self.version_vector[nid] = max(
                        self.version_vector.get(nid, 0),
                        version
                    )

            return True

        except Exception as e:
            logger.error(f"Failed to apply sync package: {e}")
            return False

    def get_conflict_status(self) -> Dict[str, Any]:
        """
        Check for synchronization conflicts.

        Returns:
            Dictionary with conflict information
        """
        return {
            'version_vector': self.version_vector,
            'pending_updates': len(self.pending_updates),
            'state_hash': self.compute_state_hash()
        }

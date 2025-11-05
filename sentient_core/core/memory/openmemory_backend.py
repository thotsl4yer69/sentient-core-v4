"""
OpenMemory backend integration for the memory system.

This module provides integration between Sentient Core's memory system
and the OpenMemory brain-inspired memory architecture with multi-sector
organization, automatic decay, and advanced retrieval capabilities.
"""

import logging
from typing import Dict, Any, Optional, List
import time

from sentient_core.integrations.openmemory.client import OpenMemory, SECTORS

logger = logging.getLogger(__name__)


class OpenMemoryBackend:
    """
    OpenMemory backend for brain-inspired memory storage.

    Features:
    - Multi-sector memory organization (episodic, semantic, procedural, emotional, reflective)
    - Automatic memory decay with sector-specific rates
    - Graph-based associations between memories
    - Vector similarity search with advanced retrieval
    - Per-user memory isolation
    - Memory reinforcement and salience tracking
    """

    # Map Sentient Core memory types to OpenMemory sectors
    MEMORY_TYPE_TO_SECTOR = {
        'short_term': 'episodic',      # Recent events and interactions
        'long_term': 'semantic',       # Facts and knowledge
        'episodic': 'episodic',        # Event memories
        'semantic': 'semantic',        # Facts and preferences
        'procedural': 'procedural',    # Habits and procedures
        'emotional': 'emotional',      # Emotional states
        'reflective': 'reflective'     # Meta-cognitive insights
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenMemory backend.

        Args:
            config: Configuration dictionary with keys:
                - openmemory.url: OpenMemory server URL (default: http://localhost:8080)
                - openmemory.api_key: Optional API key for authentication
                - openmemory.user_id: Default user ID for memory isolation
                - openmemory.auto_consolidate: Auto-consolidate memories (default: True)
        """
        self.config = config

        # OpenMemory configuration
        base_url = config.get('openmemory.url', 'http://localhost:8080')
        api_key = config.get('openmemory.api_key', '')
        self.user_id = config.get('openmemory.user_id', 'default')
        self.auto_consolidate = config.get('openmemory.auto_consolidate', True)

        # Initialize OpenMemory client
        self.client = OpenMemory(api_key=api_key, base_url=base_url)

        # Cache for statistics
        self._stats_cache = {}
        self._stats_cache_time = 0
        self._stats_cache_duration = 5.0  # Cache for 5 seconds

        logger.info(f"OpenMemory backend initialized with URL: {base_url}")

    def initialize(self):
        """Initialize and verify OpenMemory connection."""
        try:
            health = self.client.get_health()
            logger.info(f"OpenMemory backend ready: {health}")

            # Get sector information
            sectors = self.client.get_sectors()
            logger.info(f"Available sectors: {sectors}")

            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenMemory backend: {e}")
            logger.warning("Make sure OpenMemory server is running")
            return False

    def store(self, data: Any, memory_type: str = 'short_term',
              metadata: Optional[Dict[str, Any]] = None,
              importance: float = 0.5,
              user_id: Optional[str] = None) -> str:
        """
        Store data in OpenMemory.

        Args:
            data: Data to store (will be converted to string)
            memory_type: Type of memory (maps to OpenMemory sector)
            metadata: Optional metadata dictionary
            importance: Memory importance/salience (0.0-1.0)
            user_id: Optional user ID (overrides default)

        Returns:
            Memory ID
        """
        # Convert data to string content
        if isinstance(data, dict):
            content = str(data.get('content', data))
        else:
            content = str(data)

        # Map memory type to OpenMemory sector
        sector = self.MEMORY_TYPE_TO_SECTOR.get(memory_type, 'episodic')

        # Prepare metadata
        meta = metadata or {}
        meta['memory_type'] = memory_type
        meta['sector'] = sector
        meta['timestamp'] = time.time()

        # Extract tags if present
        tags = meta.pop('tags', [])
        if isinstance(tags, str):
            tags = [tags]

        # Store in OpenMemory
        try:
            result = self.client.add(
                content=content,
                tags=tags,
                metadata=meta,
                salience=importance,
                user_id=user_id or self.user_id
            )

            memory_id = result.get('id', '')
            logger.debug(f"Stored memory {memory_id} in sector {result.get('primary_sector')}")

            return memory_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    def retrieve(self, query: Any, memory_type: str = 'short_term',
                 limit: int = 10, min_score: float = 0.0,
                 user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories using vector similarity search.

        Args:
            query: Query for retrieval (string or dict)
            memory_type: Type of memory to search
            limit: Maximum number of results
            min_score: Minimum similarity score threshold
            user_id: Optional user ID for filtering

        Returns:
            List of relevant memories with scores
        """
        # Convert query to string
        if isinstance(query, dict):
            query_str = str(query.get('query', query))
        else:
            query_str = str(query)

        # Build filters
        filters = {}

        # Filter by sector if specific memory type requested
        if memory_type != 'all':
            sector = self.MEMORY_TYPE_TO_SECTOR.get(memory_type)
            if sector:
                filters['sector'] = sector

        # Add minimum score filter
        if min_score > 0:
            filters['min_score'] = min_score

        # Add user ID filter
        if user_id or self.user_id:
            filters['user_id'] = user_id or self.user_id

        # Query OpenMemory
        try:
            result = self.client.query(
                query=query_str,
                k=limit,
                filters=filters
            )

            # Convert OpenMemory format to MemorySystem format
            memories = []
            for match in result.get('matches', []):
                memory = {
                    'id': match.get('id'),
                    'data': match.get('content'),
                    'content': match.get('content'),
                    'score': match.get('score', 0.0),
                    'salience': match.get('salience', 0.5),
                    'sector': match.get('primary_sector'),
                    'timestamp': match.get('created_at'),
                    'metadata': match.get('metadata', {}),
                    'tags': match.get('tags', [])
                }
                memories.append(memory)

            logger.debug(f"Retrieved {len(memories)} memories for query: {query_str[:50]}")
            return memories

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []

    def reinforce(self, memory_id: str, boost: float = 0.2) -> bool:
        """
        Reinforce a memory by increasing its salience.

        Args:
            memory_id: ID of memory to reinforce
            boost: Amount to increase salience (0.0-1.0)

        Returns:
            Success status
        """
        try:
            result = self.client.reinforce(memory_id, boost)
            logger.debug(f"Reinforced memory {memory_id}")
            return result.get('ok', False)
        except Exception as e:
            logger.error(f"Failed to reinforce memory {memory_id}: {e}")
            return False

    def update(self, memory_id: str, content: Optional[str] = None,
               tags: Optional[List[str]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing memory.

        Args:
            memory_id: Memory ID to update
            content: New content (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)

        Returns:
            Success status
        """
        try:
            result = self.client.update(
                memory_id=memory_id,
                content=content,
                tags=tags,
                metadata=metadata
            )
            logger.debug(f"Updated memory {memory_id}")
            return result.get('ok', False)
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return False

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: Memory ID to delete

        Returns:
            Success status
        """
        try:
            result = self.client.delete(memory_id)
            logger.debug(f"Deleted memory {memory_id}")
            return result.get('ok', False)
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    def get_all(self, memory_type: str = 'all', limit: int = 100,
                offset: int = 0, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all memories with pagination.

        Args:
            memory_type: Type of memory to retrieve
            limit: Maximum number of results
            offset: Pagination offset
            user_id: Optional user ID for filtering

        Returns:
            List of memories
        """
        try:
            # Determine sector filter
            sector = None
            if memory_type != 'all':
                sector = self.MEMORY_TYPE_TO_SECTOR.get(memory_type)

            # Get memories from OpenMemory
            if user_id or self.user_id:
                result = self.client.get_user_memories(
                    user_id=user_id or self.user_id,
                    limit=limit,
                    offset=offset
                )
                items = result.get('memories', [])
            else:
                result = self.client.all(limit=limit, offset=offset, sector=sector)
                items = result.get('items', [])

            # Convert to standard format
            memories = []
            for item in items:
                memory = {
                    'id': item.get('id'),
                    'data': item.get('content'),
                    'content': item.get('content'),
                    'sector': item.get('primary_sector'),
                    'timestamp': item.get('created_at'),
                    'metadata': item.get('metadata', {}),
                    'tags': item.get('tags', []),
                    'salience': item.get('salience', 0.5)
                }
                memories.append(memory)

            return memories

        except Exception as e:
            logger.error(f"Failed to get all memories: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Statistics dictionary
        """
        # Check cache
        current_time = time.time()
        if current_time - self._stats_cache_time < self._stats_cache_duration:
            return self._stats_cache

        try:
            # Get health stats from OpenMemory
            health = self.client.get_health()
            sectors = self.client.get_sectors()

            stats = {
                'backend': 'openmemory',
                'status': health.get('status', 'unknown'),
                'sectors': sectors,
                'total_memories': sum(
                    s.get('count', 0) for s in sectors.get('sectors', {}).values()
                ),
                'user_id': self.user_id
            }

            # Update cache
            self._stats_cache = stats
            self._stats_cache_time = current_time

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                'backend': 'openmemory',
                'status': 'error',
                'error': str(e)
            }

    def consolidate(self) -> bool:
        """
        Consolidate memories (OpenMemory handles this automatically).

        OpenMemory automatically manages memory decay and consolidation,
        so this is a no-op that always returns success.

        Returns:
            Success status
        """
        logger.debug("Memory consolidation handled automatically by OpenMemory")
        return True

    def clear(self, memory_type: Optional[str] = None, user_id: Optional[str] = None) -> bool:
        """
        Clear memories.

        Note: OpenMemory doesn't support bulk deletion, so this retrieves
        all memories and deletes them individually.

        Args:
            memory_type: Type of memory to clear (None = all)
            user_id: Optional user ID for filtering

        Returns:
            Success status
        """
        try:
            # Get all memories to delete
            memories = self.get_all(
                memory_type=memory_type or 'all',
                limit=1000,
                user_id=user_id
            )

            # Delete each memory
            for memory in memories:
                self.delete(memory['id'])

            logger.info(f"Cleared {len(memories)} memories")
            return True

        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            return False

    def shutdown(self):
        """Shutdown the OpenMemory backend."""
        logger.info("OpenMemory backend shutdown")
        # OpenMemory client is stateless, no cleanup needed

"""
Memory system for storing and retrieving information.
"""

import logging
from typing import Dict, Any, Optional, List
from collections import deque
import time


logger = logging.getLogger(__name__)


class MemorySystem:
    """
    Multi-level memory system.

    Supports:
    - Short-term memory (working memory)
    - Long-term memory (persistent storage)
    - Episodic memory (events)
    - Semantic memory (facts and knowledge)
    """

    def __init__(self, config):
        """
        Initialize memory system.

        Args:
            config: Configuration object
        """
        self.config = config

        # Memory stores
        self.short_term: deque = deque(maxlen=config.get('memory.short_term.capacity', 1000))
        self.long_term: List[Dict[str, Any]] = []
        self.episodic: List[Dict[str, Any]] = []
        self.semantic: Dict[str, Any] = {}

        # Configuration
        self.backend = config.get('memory.backend', 'memory')
        self.enable_consolidation = config.get('memory.consolidation.enabled', True)

        # Vector store (if using external backend)
        self.vector_store = None

        logger.info("MemorySystem created")

    def initialize(self):
        """Initialize memory storage backend."""
        logger.info(f"Initializing memory system with backend: {self.backend}")

        if self.backend == 'chromadb':
            self._init_chromadb()
        elif self.backend == 'pinecone':
            self._init_pinecone()
        else:
            logger.info("Using in-memory storage")

    def _init_chromadb(self):
        """Initialize ChromaDB backend."""
        try:
            import chromadb

            self.vector_store = chromadb.Client()
            logger.info("ChromaDB initialized")
        except ImportError:
            logger.warning("ChromaDB not available, using in-memory storage")

    def _init_pinecone(self):
        """Initialize Pinecone backend."""
        logger.info("Pinecone backend (placeholder)")

    def store(self, data: Any, memory_type: str = 'short_term', metadata: Optional[Dict[str, Any]] = None):
        """
        Store data in memory.

        Args:
            data: Data to store
            memory_type: Type of memory (short_term, long_term, episodic, semantic)
            metadata: Optional metadata
        """
        entry = {
            'data': data,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }

        if memory_type == 'short_term':
            self.short_term.append(entry)
        elif memory_type == 'long_term':
            self.long_term.append(entry)
        elif memory_type == 'episodic':
            self.episodic.append(entry)
        elif memory_type == 'semantic':
            # For semantic, use key-value storage
            key = metadata.get('key', f'semantic_{len(self.semantic)}')
            self.semantic[key] = entry

        logger.debug(f"Stored in {memory_type} memory")

    def retrieve(self, query: Any, memory_type: str = 'short_term', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories.

        Args:
            query: Query for retrieval
            memory_type: Type of memory to search
            limit: Maximum number of results

        Returns:
            List of relevant memories
        """
        logger.debug(f"Retrieving from {memory_type} memory")

        if memory_type == 'short_term':
            return list(self.short_term)[-limit:]
        elif memory_type == 'long_term':
            return self.long_term[-limit:]
        elif memory_type == 'episodic':
            return self.episodic[-limit:]
        elif memory_type == 'semantic':
            return list(self.semantic.values())[-limit:]
        else:
            return []

    def consolidate(self):
        """Consolidate short-term memories to long-term storage."""
        if not self.enable_consolidation:
            return

        logger.info("Consolidating memories...")

        # Move important short-term memories to long-term
        threshold = self.config.get('memory.consolidation.importance_threshold', 0.6)

        for entry in list(self.short_term):
            importance = entry.get('metadata', {}).get('importance', 0.5)

            if importance >= threshold:
                self.long_term.append(entry)
                logger.debug("Memory consolidated to long-term storage")

    def clear(self, memory_type: Optional[str] = None):
        """
        Clear memory.

        Args:
            memory_type: Type of memory to clear (None = all)
        """
        if memory_type is None or memory_type == 'short_term':
            self.short_term.clear()

        if memory_type is None or memory_type == 'long_term':
            self.long_term.clear()

        if memory_type is None or memory_type == 'episodic':
            self.episodic.clear()

        if memory_type is None or memory_type == 'semantic':
            self.semantic.clear()

        logger.info(f"Cleared {memory_type or 'all'} memory")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            'short_term_count': len(self.short_term),
            'long_term_count': len(self.long_term),
            'episodic_count': len(self.episodic),
            'semantic_count': len(self.semantic),
            'backend': self.backend
        }

    def shutdown(self):
        """Shutdown memory system."""
        logger.info("Shutting down memory system...")

        # Optionally persist memories
        # ... persistence logic ...

        self.clear()

        logger.info("Memory system shutdown complete")

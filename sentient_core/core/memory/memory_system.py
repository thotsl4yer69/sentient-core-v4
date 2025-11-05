"""
Memory system for storing and retrieving information.
"""

import logging
from typing import Dict, Any, Optional, List
from collections import deque
import time


logger = logging.getLogger(__name__)


# Import OpenMemory backend if available
try:
    from sentient_core.core.memory.openmemory_backend import OpenMemoryBackend
    OPENMEMORY_AVAILABLE = True
except ImportError:
    OPENMEMORY_AVAILABLE = False
    logger.warning("OpenMemory backend not available")


class MemorySystem:
    """
    Multi-level memory system.

    Supports:
    - Short-term memory (working memory)
    - Long-term memory (persistent storage)
    - Episodic memory (events)
    - Semantic memory (facts and knowledge)
    - Procedural memory (habits, procedures)
    - Emotional memory (sentiment states)
    - Reflective memory (meta-cognitive insights)

    Backends:
    - memory: In-memory storage (default)
    - chromadb: ChromaDB vector database
    - pinecone: Pinecone vector database
    - openmemory: OpenMemory brain-inspired memory system
    """

    def __init__(self, config):
        """
        Initialize memory system.

        Args:
            config: Configuration object
        """
        self.config = config

        # Memory stores (for in-memory backend)
        self.short_term: deque = deque(maxlen=config.get('memory.short_term.capacity', 1000))
        self.long_term: List[Dict[str, Any]] = []
        self.episodic: List[Dict[str, Any]] = []
        self.semantic: Dict[str, Any] = {}

        # Configuration
        self.backend = config.get('memory.backend', 'memory')
        self.enable_consolidation = config.get('memory.consolidation.enabled', True)

        # Backend instances
        self.vector_store = None
        self.openmemory_backend = None

        logger.info(f"MemorySystem created with backend: {self.backend}")

    def initialize(self):
        """Initialize memory storage backend."""
        logger.info(f"Initializing memory system with backend: {self.backend}")

        if self.backend == 'chromadb':
            self._init_chromadb()
        elif self.backend == 'pinecone':
            self._init_pinecone()
        elif self.backend == 'openmemory':
            self._init_openmemory()
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

    def _init_openmemory(self):
        """Initialize OpenMemory backend."""
        if not OPENMEMORY_AVAILABLE:
            logger.error("OpenMemory backend requested but not available")
            logger.info("Falling back to in-memory storage")
            self.backend = 'memory'
            return

        try:
            self.openmemory_backend = OpenMemoryBackend(self.config)
            success = self.openmemory_backend.initialize()

            if success:
                logger.info("OpenMemory backend initialized successfully")
            else:
                logger.warning("OpenMemory backend initialization failed, falling back to in-memory")
                self.backend = 'memory'
                self.openmemory_backend = None

        except Exception as e:
            logger.error(f"Failed to initialize OpenMemory backend: {e}")
            logger.info("Falling back to in-memory storage")
            self.backend = 'memory'
            self.openmemory_backend = None

    def store(self, data: Any, memory_type: str = 'short_term', metadata: Optional[Dict[str, Any]] = None):
        """
        Store data in memory.

        Args:
            data: Data to store
            memory_type: Type of memory (short_term, long_term, episodic, semantic, procedural, emotional, reflective)
            metadata: Optional metadata

        Returns:
            Memory ID (for OpenMemory backend) or None
        """
        # Delegate to OpenMemory backend if configured
        if self.openmemory_backend is not None:
            importance = (metadata or {}).get('importance', 0.5)
            return self.openmemory_backend.store(
                data=data,
                memory_type=memory_type,
                metadata=metadata,
                importance=importance
            )

        # Default in-memory storage
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
            key = (metadata or {}).get('key', f'semantic_{len(self.semantic)}')
            self.semantic[key] = entry

        logger.debug(f"Stored in {memory_type} memory")
        return None

    def retrieve(self, query: Any, memory_type: str = 'short_term', limit: int = 10,
                 min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories.

        Args:
            query: Query for retrieval
            memory_type: Type of memory to search
            limit: Maximum number of results
            min_score: Minimum similarity score (for vector backends)

        Returns:
            List of relevant memories
        """
        # Delegate to OpenMemory backend if configured
        if self.openmemory_backend is not None:
            return self.openmemory_backend.retrieve(
                query=query,
                memory_type=memory_type,
                limit=limit,
                min_score=min_score
            )

        # Default in-memory retrieval
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
        # Delegate to OpenMemory backend if configured
        if self.openmemory_backend is not None:
            return self.openmemory_backend.consolidate()

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
        # Delegate to OpenMemory backend if configured
        if self.openmemory_backend is not None:
            self.openmemory_backend.clear(memory_type=memory_type)
            return

        # Default in-memory clearing
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
        # Delegate to OpenMemory backend if configured
        if self.openmemory_backend is not None:
            return self.openmemory_backend.get_stats()

        # Default in-memory stats
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

        # Shutdown OpenMemory backend if configured
        if self.openmemory_backend is not None:
            self.openmemory_backend.shutdown()
            return

        # Default in-memory shutdown
        # Optionally persist memories
        # ... persistence logic ...

        self.clear()

        logger.info("Memory system shutdown complete")

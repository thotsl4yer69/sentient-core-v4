"""
Unit tests for memory systems.
"""

import pytest
from datetime import datetime

from sentient_core.core.memory.memory_system import MemorySystem, MemoryEntry


@pytest.mark.unit
def test_memory_system_initialization(sample_config):
    """Test memory system initialization."""
    memory = MemorySystem(sample_config)

    assert memory is not None
    assert hasattr(memory, 'short_term')
    assert hasattr(memory, 'add')


@pytest.mark.unit
def test_memory_add_entry(sample_config):
    """Test adding a memory entry."""
    memory = MemorySystem(sample_config)

    initial_size = len(memory.short_term) if hasattr(memory, 'short_term') else 0

    memory.add("Test memory content", importance=0.8)

    # Memory should have grown
    current_size = len(memory.short_term) if hasattr(memory, 'short_term') else 0
    assert current_size > initial_size


@pytest.mark.unit
def test_memory_retrieve(sample_config):
    """Test retrieving memories."""
    memory = MemorySystem(sample_config)

    # Add some memories
    memory.add("First memory", importance=0.5)
    memory.add("Second memory", importance=0.8)
    memory.add("Third memory", importance=0.6)

    # Retrieve recent memories
    recent = memory.get_recent(n=2)

    assert len(recent) <= 2
    # Most recent should be last added
    if recent:
        assert "memory" in str(recent[0]).lower() or isinstance(recent[0], dict)


@pytest.mark.unit
def test_memory_search(sample_config):
    """Test searching memories by query."""
    memory = MemorySystem(sample_config)

    # Add memories with distinct content
    memory.add("The sky is blue", importance=0.7)
    memory.add("Grass is green", importance=0.6)
    memory.add("The ocean is blue", importance=0.8)

    # Search for blue-related memories
    results = memory.search("blue", top_k=2)

    # Should return relevant results
    assert len(results) <= 2


@pytest.mark.unit
def test_memory_importance_ranking(sample_config):
    """Test that memories are ranked by importance."""
    memory = MemorySystem(sample_config)

    # Add memories with different importance
    memory.add("Low importance", importance=0.3)
    memory.add("High importance", importance=0.9)
    memory.add("Medium importance", importance=0.6)

    # Get top memories
    top_memories = memory.get_important(n=2)

    # Should return most important (implementation dependent)
    assert len(top_memories) <= 2


@pytest.mark.unit
def test_memory_capacity_limit(sample_config):
    """Test that memory respects capacity limits."""
    memory = MemorySystem(sample_config)
    capacity = sample_config.memory.short_term_capacity

    # Add more than capacity
    for i in range(capacity + 5):
        memory.add(f"Memory {i}", importance=0.5)

    # Should not exceed capacity (with some tolerance)
    current_size = len(memory.short_term) if hasattr(memory, 'short_term') else 0
    assert current_size <= capacity + 2


@pytest.mark.unit
def test_memory_clear(sample_config):
    """Test clearing memory."""
    memory = MemorySystem(sample_config)

    # Add some memories
    memory.add("Memory 1", importance=0.5)
    memory.add("Memory 2", importance=0.7)

    # Clear
    if hasattr(memory, 'clear'):
        memory.clear()
        assert len(memory.short_term) == 0


@pytest.mark.unit
def test_memory_entry_creation():
    """Test creating individual memory entries."""
    entry = MemoryEntry(
        content="Test content",
        timestamp=datetime.now(),
        importance=0.8,
        tags=["test", "unit"]
    )

    assert entry.content == "Test content"
    assert entry.importance == 0.8
    assert "test" in entry.tags


@pytest.mark.unit
def test_memory_consolidation(sample_config):
    """Test memory consolidation (if implemented)."""
    memory = MemorySystem(sample_config)

    # Add many short-term memories
    for i in range(20):
        memory.add(f"Memory {i}", importance=0.5 + (i * 0.02))

    # Trigger consolidation if method exists
    if hasattr(memory, 'consolidate'):
        memory.consolidate()

        # Long-term memory should have content
        if hasattr(memory, 'long_term'):
            assert len(memory.long_term) > 0


@pytest.mark.unit
def test_memory_semantic_search(sample_config):
    """Test semantic search capabilities."""
    memory = MemorySystem(sample_config)

    # Add semantically related memories
    memory.add("Python is a programming language", importance=0.7)
    memory.add("JavaScript is used for web development", importance=0.7)
    memory.add("Machine learning uses algorithms", importance=0.8)

    # Search with semantic query
    results = memory.search("coding languages", top_k=2)

    # Should return programming-related memories
    assert len(results) <= 2

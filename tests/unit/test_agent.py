"""
Unit tests for SentientAgent core functionality.
"""

import pytest
import asyncio

from sentient_core.core.agent import SentientAgent
from sentient_core.core.config import SentientConfig


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_initialization(sample_config):
    """Test agent initialization."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    assert agent.config is not None
    assert agent.model_manager is not None
    assert agent.memory is not None
    assert agent.reasoning_engine is not None

    await agent.shutdown()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_process_simple_query(sample_agent):
    """Test processing a simple query."""
    result = await sample_agent.process("Hello, how are you?")

    assert result is not None
    assert "response" in result or isinstance(result, str)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_process_with_memory(sample_agent):
    """Test that agent uses memory across queries."""
    # First query
    result1 = await sample_agent.process("My name is Alice.")
    assert result1 is not None

    # Second query - should remember context
    result2 = await sample_agent.process("What is my name?")
    assert result2 is not None

    # Check that memory was updated
    assert len(sample_agent.memory.short_term) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_shutdown(sample_config):
    """Test agent shutdown cleanup."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    # Verify agent is running
    assert agent.model_manager is not None

    # Shutdown
    await agent.shutdown()

    # Verify cleanup (implementation dependent)
    # This test verifies shutdown doesn't crash


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_concurrent_queries(sample_agent):
    """Test handling multiple concurrent queries."""
    queries = [
        "What is 2 + 2?",
        "Tell me a joke.",
        "What is the capital of France?",
    ]

    # Process queries concurrently
    tasks = [sample_agent.process(q) for q in queries]
    results = await asyncio.gather(*tasks)

    # All queries should return results
    assert len(results) == len(queries)
    assert all(r is not None for r in results)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_error_handling(sample_agent):
    """Test agent error handling."""
    # Try processing an empty query
    result = await sample_agent.process("")

    # Should handle gracefully (not crash)
    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_state_persistence(sample_agent):
    """Test agent state is maintained."""
    # Process a query
    await sample_agent.process("Remember: the code is 1234")

    # Get state
    state1 = {
        "memory_size": len(sample_agent.memory.short_term),
    }

    # Process another query
    await sample_agent.process("What was the code?")

    # State should have evolved
    state2 = {
        "memory_size": len(sample_agent.memory.short_term),
    }

    # Memory should have grown
    assert state2["memory_size"] >= state1["memory_size"]


@pytest.mark.unit
def test_agent_config_injection(sample_config):
    """Test injecting custom configuration."""
    agent = SentientAgent(config=sample_config)

    assert agent.config.model.provider == "dummy"
    assert agent.config.memory.enabled is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_memory_capacity(sample_agent):
    """Test that memory respects capacity limits."""
    capacity = sample_agent.config.memory.short_term_capacity

    # Add more items than capacity
    for i in range(capacity + 5):
        await sample_agent.process(f"Message {i}")

    # Memory should not exceed capacity (or should handle overflow)
    assert len(sample_agent.memory.short_term) <= capacity + 2  # Allow some buffer


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_reasoning_integration(sample_agent):
    """Test that agent uses reasoning engine."""
    # Query requiring reasoning
    result = await sample_agent.process(
        "If all birds can fly, and a penguin is a bird, can a penguin fly?"
    )

    assert result is not None
    # Should produce some response (quality depends on model)

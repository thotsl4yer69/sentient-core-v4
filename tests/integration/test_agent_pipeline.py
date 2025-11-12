"""
Integration tests for complete agent pipeline.
"""

import pytest
import asyncio

from sentient_core.core.agent import SentientAgent
from sentient_core.core.config import SentientConfig


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_pipeline_simple_query(sample_config):
    """Test complete pipeline with a simple query."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    # Process a query through full pipeline
    result = await agent.process("What is 2 + 2?")

    # Should get a response
    assert result is not None

    # Check that all components were used
    assert len(agent.memory.short_term) > 0

    await agent.shutdown()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_with_reasoning(sample_config):
    """Test pipeline with reasoning component."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    query = "If it's raining and I don't have an umbrella, what should I do?"
    result = await agent.process(query)

    assert result is not None

    await agent.shutdown()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_memory_persistence(sample_config):
    """Test that memory persists across queries."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    # First interaction
    await agent.process("My favorite color is blue.")

    # Second interaction - should remember
    result = await agent.process("What is my favorite color?")

    assert result is not None

    # Memory should contain both interactions
    assert len(agent.memory.short_term) >= 2

    await agent.shutdown()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_concurrent_processing(sample_config):
    """Test pipeline handling concurrent requests."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    queries = [
        "What is Python?",
        "Explain machine learning.",
        "What is a neural network?",
    ]

    # Process concurrently
    tasks = [agent.process(q) for q in queries]
    results = await asyncio.gather(*tasks)

    # All should complete successfully
    assert len(results) == len(queries)
    assert all(r is not None for r in results)

    await agent.shutdown()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_with_actions(sample_config):
    """Test pipeline with action execution."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    # Query that might trigger action
    result = await agent.process("Calculate the square root of 16")

    assert result is not None

    await agent.shutdown()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_error_recovery(sample_config):
    """Test pipeline error recovery."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    # Try problematic input
    result = await agent.process("")

    # Should handle gracefully
    assert result is not None

    # Agent should still be functional
    result2 = await agent.process("Hello")
    assert result2 is not None

    await agent.shutdown()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_state_consistency(sample_config):
    """Test that pipeline maintains consistent state."""
    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    # Multiple interactions
    for i in range(5):
        await agent.process(f"Message {i}")

    # Check state consistency
    assert len(agent.memory.short_term) >= 5

    # State should be coherent
    memory_timestamps = []
    for entry in agent.memory.short_term:
        if isinstance(entry, dict) and "timestamp" in entry:
            memory_timestamps.append(entry["timestamp"])

    # Timestamps should be in order (if present)
    if len(memory_timestamps) > 1:
        assert memory_timestamps == sorted(memory_timestamps)

    await agent.shutdown()


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_pipeline_long_conversation(sample_config):
    """Test pipeline with long conversation."""
    # Increase capacity for this test
    sample_config.memory.short_term_capacity = 50

    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    # Simulate long conversation
    for i in range(30):
        await agent.process(f"Statement number {i}")

    # Should handle without issues
    assert len(agent.memory.short_term) > 0

    # Should still respond coherently
    result = await agent.process("Summarize our conversation")
    assert result is not None

    await agent.shutdown()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_with_hardware(sample_config):
    """Test pipeline with hardware acceleration."""
    sample_config.hardware.auto_detect = True

    agent = SentientAgent(config=sample_config)
    await agent.initialize()

    result = await agent.process("Test query with hardware")

    assert result is not None

    # Check hardware was initialized
    if hasattr(agent, 'hardware_manager'):
        assert agent.hardware_manager is not None

    await agent.shutdown()

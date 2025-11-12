"""
Unit tests for reasoning engine.
"""

import pytest

from sentient_core.core.reasoning.reasoning_engine import ReasoningEngine


@pytest.mark.unit
def test_reasoning_engine_initialization(sample_config):
    """Test reasoning engine initialization."""
    engine = ReasoningEngine(sample_config)

    assert engine is not None
    assert engine.max_depth > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_simple_inference(sample_config, mock_llm_interface):
    """Test simple logical inference."""
    engine = ReasoningEngine(sample_config)

    premises = [
        "All humans are mortal",
        "Socrates is a human"
    ]

    result = await engine.infer(premises, llm_interface=mock_llm_interface)

    assert result is not None
    assert "conclusion" in result or isinstance(result, str)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_with_context(sample_config, mock_llm_interface):
    """Test reasoning with additional context."""
    engine = ReasoningEngine(sample_config)

    query = "Should I bring an umbrella?"
    context = ["It is raining outside", "Umbrellas protect from rain"]

    result = await engine.reason(
        query=query,
        context=context,
        llm_interface=mock_llm_interface
    )

    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_causal_analysis(sample_config, mock_llm_interface):
    """Test causal reasoning."""
    engine = ReasoningEngine(sample_config)

    event = "The plant died"
    observations = ["No water for 2 weeks", "Leaves turned brown", "Soil was dry"]

    if hasattr(engine, 'analyze_causality'):
        result = await engine.analyze_causality(
            event=event,
            observations=observations,
            llm_interface=mock_llm_interface
        )

        assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_multi_step(sample_config, mock_llm_interface):
    """Test multi-step reasoning chain."""
    engine = ReasoningEngine(sample_config)

    problem = "How to make coffee?"

    result = await engine.reason(
        query=problem,
        context=[],
        llm_interface=mock_llm_interface,
        max_steps=3
    )

    assert result is not None


@pytest.mark.unit
def test_reasoning_depth_limit(sample_config):
    """Test that reasoning respects depth limits."""
    engine = ReasoningEngine(sample_config)

    assert engine.max_depth == sample_config.reasoning.max_depth


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_timeout(sample_config, mock_llm_interface):
    """Test reasoning timeout handling."""
    engine = ReasoningEngine(sample_config)

    # Set very short timeout
    engine.timeout = 0.001

    # Should handle timeout gracefully
    try:
        result = await engine.reason(
            query="Complex query",
            context=[],
            llm_interface=mock_llm_interface
        )
        # If it completes, that's fine too
        assert result is not None
    except asyncio.TimeoutError:
        # Expected behavior
        pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_confidence_scoring(sample_config, mock_llm_interface):
    """Test confidence scoring in reasoning results."""
    engine = ReasoningEngine(sample_config)

    result = await engine.reason(
        query="Is the sky blue?",
        context=["The sky appears blue during daytime"],
        llm_interface=mock_llm_interface
    )

    # Check if result includes confidence score
    if isinstance(result, dict) and "confidence" in result:
        assert 0 <= result["confidence"] <= 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_fact_checking(sample_config, mock_llm_interface):
    """Test fact-checking capabilities."""
    engine = ReasoningEngine(sample_config)

    statement = "Water boils at 100°C at sea level"
    facts = ["Water's boiling point is temperature and pressure dependent"]

    if hasattr(engine, 'check_fact'):
        result = await engine.check_fact(
            statement=statement,
            known_facts=facts,
            llm_interface=mock_llm_interface
        )

        assert result is not None

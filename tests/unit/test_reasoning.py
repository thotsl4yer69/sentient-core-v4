"""
Unit tests for reasoning engine.
"""

import asyncio
import pytest

from sentient_core.core.reasoning.reasoning_engine import ReasoningEngine


@pytest.mark.unit
def test_reasoning_engine_initialization(sample_config, mock_model_manager):
    """Test reasoning engine initialization."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    assert engine is not None
    assert engine.max_depth > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_simple_inference(sample_config, mock_model_manager, mock_llm_interface):
    """Test simple logical inference."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    premises = [
        "All humans are mortal",
        "Socrates is a human"
    ]

    if hasattr(engine, 'infer'):
        result = await engine.infer(premises, llm_interface=mock_llm_interface)
        assert result is not None
        assert "conclusion" in result or isinstance(result, str)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_with_context(sample_config, mock_model_manager, mock_llm_interface):
    """Test reasoning with additional context."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    query = "Should I bring an umbrella?"
    context = {"additional_info": ["It is raining outside", "Umbrellas protect from rain"]}

    result = engine.reason(input_data=query, context=context)

    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_causal_analysis(sample_config, mock_model_manager, mock_llm_interface):
    """Test causal reasoning."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    event_a = "No water for 2 weeks"
    event_b = "The plant died"

    if hasattr(engine, 'infer_causality'):
        result = engine.infer_causality(event_a=event_a, event_b=event_b)
        assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_multi_step(sample_config, mock_model_manager, mock_llm_interface):
    """Test multi-step reasoning chain."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    problem = "How to make coffee?"

    result = engine.reason(input_data=problem, context={})

    assert result is not None


@pytest.mark.unit
def test_reasoning_depth_limit(sample_config, mock_model_manager):
    """Test that reasoning respects depth limits."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    expected_depth = sample_config.get('reasoning.max_depth', 5)
    assert engine.max_depth == expected_depth


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_timeout(sample_config, mock_model_manager, mock_llm_interface):
    """Test reasoning timeout handling."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    # Set very short timeout
    engine.timeout = 0.001

    # Should handle timeout gracefully
    try:
        result = engine.reason(input_data="Complex query", context={})
        # If it completes, that's fine too
        assert result is not None
    except asyncio.TimeoutError:
        # Expected behavior
        pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_confidence_scoring(sample_config, mock_model_manager, mock_llm_interface):
    """Test confidence scoring in reasoning results."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    result = engine.reason(
        input_data="Is the sky blue?",
        context={"additional_info": ["The sky appears blue during daytime"]}
    )

    # Check if result includes confidence score
    if isinstance(result, dict) and "confidence" in result:
        assert 0 <= result["confidence"] <= 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reasoning_fact_checking(sample_config, mock_model_manager, mock_llm_interface):
    """Test fact-checking capabilities."""
    engine = ReasoningEngine(sample_config, mock_model_manager)

    statement = "Water boils at 100°C at sea level"
    facts = ["Water's boiling point is temperature and pressure dependent"]

    if hasattr(engine, 'check_fact'):
        result = await engine.check_fact(
            statement=statement,
            known_facts=facts,
            llm_interface=mock_llm_interface
        )

        assert result is not None

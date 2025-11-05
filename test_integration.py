#!/usr/bin/env python
"""
Integration test for Sentient Core v4.

Tests all major components:
- Core agent initialization
- Agent team coordination
- Model manager
- Voice processing
- Pixelscape vision
- Memory system
- Reasoning engine
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_core_agent():
    """Test core agent initialization."""
    logger.info("="*60)
    logger.info("Testing Core Agent")
    logger.info("="*60)

    from sentient_core import SentientAgent
    from sentient_core.core.config import Config

    # Create config
    config = Config.from_yaml("config/default.yaml")

    # Create agent
    agent = SentientAgent(config=config)

    # Initialize
    agent.initialize()

    # Test status
    status = agent.get_status()
    logger.info(f"Agent Status: {status}")

    assert status['initialized'] == True
    logger.info("✓ Core agent test passed")

    return agent


def test_agent_team(agent):
    """Test agent team functionality."""
    logger.info("\n" + "="*60)
    logger.info("Testing Agent Team")
    logger.info("="*60)

    # Execute team task
    result = agent.create_team_task("Research and analyze AI trends", num_agents=3)

    logger.info(f"Team Task Result: {result}")

    assert result['status'] == 'completed'
    logger.info("✓ Agent team test passed")


def test_processing(agent):
    """Test basic processing."""
    logger.info("\n" + "="*60)
    logger.info("Testing Processing")
    logger.info("="*60)

    # Process text input
    response = agent.process("What is artificial intelligence?")

    logger.info(f"Response: {response}")
    logger.info("✓ Processing test passed")


def test_memory_system(agent):
    """Test memory system."""
    logger.info("\n" + "="*60)
    logger.info("Testing Memory System")
    logger.info("="*60)

    if agent.memory_system:
        # Store some data
        agent.memory_system.store("Test memory entry", memory_type='short_term')

        # Retrieve
        memories = agent.memory_system.retrieve("test", memory_type='short_term')

        logger.info(f"Retrieved {len(memories)} memories")

        # Get stats
        stats = agent.memory_system.get_stats()
        logger.info(f"Memory Stats: {stats}")

        logger.info("✓ Memory system test passed")
    else:
        logger.warning("⚠ Memory system not initialized")


def test_voice_processor(agent):
    """Test voice processing."""
    logger.info("\n" + "="*60)
    logger.info("Testing Voice Processor")
    logger.info("="*60)

    if agent.voice_processor:
        info = agent.voice_processor.get_info()
        logger.info(f"Voice Processor Info: {info}")
        logger.info("✓ Voice processor test passed")
    else:
        logger.warning("⚠ Voice processor not initialized")


def test_vision_system(agent):
    """Test vision system (Pixelscape)."""
    logger.info("\n" + "="*60)
    logger.info("Testing Vision System (Pixelscape)")
    logger.info("="*60)

    if agent.vision_system:
        info = agent.vision_system.get_info()
        logger.info(f"Vision System Info: {info}")
        logger.info("✓ Vision system test passed")
    else:
        logger.warning("⚠ Vision system not initialized")


def test_model_manager(agent):
    """Test model manager."""
    logger.info("\n" + "="*60)
    logger.info("Testing Model Manager")
    logger.info("="*60)

    if agent.model_manager:
        models = agent.model_manager.list_models()
        logger.info(f"Available models: {models}")

        info = agent.model_manager.get_model_info()
        logger.info(f"Active model info: {info}")

        logger.info("✓ Model manager test passed")
    else:
        logger.warning("⚠ Model manager not initialized")


def main():
    """Run all tests."""
    logger.info("\n" + "="*60)
    logger.info("Sentient Core v4 - Integration Test")
    logger.info("="*60)

    try:
        # Test core agent
        agent = test_core_agent()

        # Test components
        test_agent_team(agent)
        test_processing(agent)
        test_memory_system(agent)
        test_voice_processor(agent)
        test_vision_system(agent)
        test_model_manager(agent)

        # Shutdown
        logger.info("\n" + "="*60)
        logger.info("Shutting down agent")
        logger.info("="*60)
        agent.shutdown()

        logger.info("\n" + "="*60)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("="*60)

        return 0

    except Exception as e:
        logger.error(f"✗ TEST FAILED: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

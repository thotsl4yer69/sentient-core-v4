"""
Pytest configuration and shared fixtures for Sentient Core tests.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Dict, Any
from unittest.mock import MagicMock, AsyncMock

import pytest
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentient_core.core.config import SentientConfig
from sentient_core.core.agent import SentientAgent
from sentient_core.models.llm_interface import DummyLLMInterface


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_dict() -> Dict[str, Any]:
    """Return a sample configuration dictionary."""
    return {
        "model": {
            "provider": "dummy",
            "name": "test-model",
            "temperature": 0.7,
            "max_tokens": 512,
            "context_window": 4096,
        },
        "memory": {
            "enabled": True,
            "short_term_capacity": 10,
            "long_term_enabled": False,
            "use_vector_db": False,
        },
        "reasoning": {
            "max_depth": 3,
            "timeout": 30,
        },
        "hardware": {
            "auto_detect": False,
            "preferred": "cpu",
        },
        "distributed": {
            "enabled": False,
            "node_id": "test-node",
            "discovery_port": 5000,
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "enable_cors": True,
        },
        "logging": {
            "level": "INFO",
            "file": None,
        },
    }


@pytest.fixture
def sample_config(temp_dir, sample_config_dict) -> SentientConfig:
    """Create a sample configuration file and return SentientConfig object."""
    config_file = temp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config_dict, f)

    return SentientConfig(config_file)


@pytest.fixture
def mock_llm_interface():
    """Create a mock LLM interface for testing."""
    interface = DummyLLMInterface()
    return interface


@pytest.fixture
def mock_model_manager():
    """Create a mock model manager for testing."""
    mock = MagicMock()
    mock.get_model = MagicMock(return_value=None)
    mock.interface = None
    return mock


@pytest.fixture
async def sample_agent(sample_config, mock_llm_interface) -> AsyncGenerator[SentientAgent, None]:
    """Create a sample SentientAgent for testing."""
    agent = SentientAgent(config=sample_config)
    agent.model_manager.interface = mock_llm_interface
    await agent.initialize()
    yield agent
    await agent.shutdown()


@pytest.fixture
def mock_hardware_interface():
    """Create a mock hardware interface."""
    mock = MagicMock()
    mock.initialize = AsyncMock(return_value=True)
    mock.is_available = MagicMock(return_value=True)
    mock.get_status = MagicMock(return_value={"status": "ok", "utilization": 0.5})
    mock.shutdown = AsyncMock()
    return mock


@pytest.fixture
def mock_memory_entry():
    """Create a sample memory entry."""
    return {
        "content": "Test memory content",
        "timestamp": "2025-11-12T10:00:00",
        "importance": 0.8,
        "tags": ["test", "sample"],
        "embedding": [0.1] * 768,
    }


@pytest.fixture
def mock_sensor_data():
    """Create sample sensor data."""
    return {
        "rf": {
            "frequencies": [2400.0, 2450.0, 2500.0],
            "power_levels": [-70, -65, -80],
            "timestamp": "2025-11-12T10:00:00",
        },
        "health": {
            "cpu_percent": 45.2,
            "memory_percent": 60.5,
            "disk_percent": 70.0,
            "temperature": 55.0,
            "timestamp": "2025-11-12T10:00:00",
        },
    }


@pytest.fixture
def mock_perception_result():
    """Create a sample perception result."""
    return {
        "text": "Sample input text for testing",
        "entities": [
            {"text": "testing", "type": "CONCEPT", "confidence": 0.9}
        ],
        "sentiment": {"polarity": 0.5, "subjectivity": 0.3},
        "language": "en",
    }


@pytest.fixture
def mock_reasoning_result():
    """Create a sample reasoning result."""
    return {
        "conclusion": "Test conclusion based on reasoning",
        "confidence": 0.85,
        "reasoning_chain": [
            {"step": 1, "premise": "Test premise 1", "conclusion": "Intermediate conclusion 1"},
            {"step": 2, "premise": "Intermediate conclusion 1", "conclusion": "Test conclusion"},
        ],
        "facts_used": ["fact1", "fact2"],
    }


@pytest.fixture
def mock_distributed_state():
    """Create a sample distributed state."""
    return {
        "node_id": "test-node-1",
        "timestamp": "2025-11-12T10:00:00",
        "status": "active",
        "current_task": "test-task",
        "emotional_state": {
            "valence": 0.5,
            "arousal": 0.3,
            "dominance": 0.6,
        },
        "metrics": {
            "tasks_completed": 10,
            "uptime_seconds": 3600,
        },
    }


@pytest.fixture
def mock_action_result():
    """Create a sample action execution result."""
    return {
        "action": "test_action",
        "success": True,
        "result": "Action executed successfully",
        "timestamp": "2025-11-12T10:00:00",
        "duration_ms": 150,
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as requiring asyncio"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "hardware: mark test as requiring hardware"
    )


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_model_file(temp_dir):
    """Create a mock model file for testing."""
    model_file = temp_dir / "test_model.gguf"
    model_file.write_text("Mock model file content")
    return model_file

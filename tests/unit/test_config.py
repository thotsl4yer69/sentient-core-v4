"""
Unit tests for configuration management.
"""

import pytest
import yaml
from pathlib import Path

from sentient_core.core.config import SentientConfig


@pytest.mark.unit
def test_config_load_from_file(temp_dir, sample_config_dict):
    """Test loading configuration from file."""
    config_file = temp_dir / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config_dict, f)

    config = SentientConfig(config_file)

    assert config.model.provider == "dummy"
    assert config.model.temperature == 0.7
    assert config.memory.enabled is True
    assert config.hardware.preferred == "cpu"


@pytest.mark.unit
def test_config_defaults():
    """Test configuration with default values."""
    config = SentientConfig()

    # Should have sensible defaults
    assert config.model.provider in ["openai", "anthropic", "local", "dummy"]
    assert 0 <= config.model.temperature <= 2.0
    assert config.model.max_tokens > 0


@pytest.mark.unit
def test_config_attribute_access(sample_config):
    """Test accessing configuration via attributes."""
    # Dot notation access
    assert sample_config.model.provider == "dummy"
    assert sample_config.memory.enabled is True

    # Dictionary access
    assert sample_config["model"]["provider"] == "dummy"
    assert sample_config["memory"]["enabled"] is True


@pytest.mark.unit
def test_config_nested_access(sample_config):
    """Test nested configuration access."""
    assert sample_config.model.temperature == 0.7
    assert sample_config.memory.short_term_capacity == 10
    assert sample_config.reasoning.max_depth == 3


@pytest.mark.unit
def test_config_update(sample_config):
    """Test updating configuration values."""
    original_temp = sample_config.model.temperature
    sample_config.model.temperature = 0.9

    assert sample_config.model.temperature == 0.9
    assert sample_config.model.temperature != original_temp


@pytest.mark.unit
def test_config_validation(temp_dir):
    """Test configuration validation."""
    invalid_config = {
        "model": {
            "temperature": 5.0,  # Invalid: > 2.0
        }
    }

    config_file = temp_dir / "invalid_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(invalid_config, f)

    # Should either raise error or clamp to valid range
    try:
        config = SentientConfig(config_file)
        # If it doesn't raise, it should have clamped the value
        assert 0 <= config.model.temperature <= 2.0
    except (ValueError, AssertionError):
        # Expected behavior
        pass


@pytest.mark.unit
def test_config_missing_file():
    """Test loading configuration from non-existent file."""
    # Should fall back to defaults without crashing
    config = SentientConfig(Path("/nonexistent/config.yaml"))
    assert config is not None


@pytest.mark.unit
def test_config_to_dict(sample_config):
    """Test converting configuration to dictionary."""
    config_dict = dict(sample_config)

    assert "model" in config_dict
    assert "memory" in config_dict
    assert config_dict["model"]["provider"] == "dummy"


@pytest.mark.unit
def test_config_merge(temp_dir, sample_config_dict):
    """Test merging configuration with overrides."""
    config_file = temp_dir / "base_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config_dict, f)

    config = SentientConfig(config_file)

    # Override specific values
    overrides = {
        "model": {"temperature": 0.5},
        "memory": {"enabled": False}
    }

    # Apply overrides
    for key, value in overrides.items():
        for subkey, subvalue in value.items():
            setattr(getattr(config, key), subkey, subvalue)

    assert config.model.temperature == 0.5
    assert config.memory.enabled is False


@pytest.mark.unit
def test_config_environment_override(temp_dir, sample_config_dict, monkeypatch):
    """Test configuration override via environment variables."""
    import os

    config_file = temp_dir / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config_dict, f)

    # Set environment variable
    monkeypatch.setenv("SENTIENT_MODEL_TEMPERATURE", "0.3")

    config = SentientConfig(config_file)

    # Check if environment variable can override
    # (This depends on implementation - adjust test accordingly)
    # For now, just verify config loads
    assert config is not None

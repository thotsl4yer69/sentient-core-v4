"""
Unit tests for hardware abstraction layer.
"""

import pytest

from sentient_core.hardware.manager import HardwareManager
from sentient_core.hardware.hailo_interface import HailoInterface
from sentient_core.hardware.coral_interface import CoralInterface


@pytest.mark.unit
def test_hardware_manager_initialization(sample_config):
    """Test hardware manager initialization."""
    manager = HardwareManager(sample_config)

    assert manager is not None
    assert hasattr(manager, 'available_devices')


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hardware_auto_detection(sample_config):
    """Test automatic hardware detection."""
    sample_config.hardware.auto_detect = True
    manager = HardwareManager(sample_config)

    await manager.initialize()

    # Should have detected something (at least CPU)
    assert len(manager.available_devices) > 0

    await manager.shutdown()


@pytest.mark.unit
@pytest.mark.hardware
def test_hailo_interface_availability():
    """Test Hailo interface availability detection."""
    interface = HailoInterface()

    # Should return boolean without crashing
    is_available = interface.is_available()
    assert isinstance(is_available, bool)


@pytest.mark.unit
@pytest.mark.hardware
def test_coral_interface_availability():
    """Test Coral TPU interface availability detection."""
    interface = CoralInterface()

    # Should return boolean without crashing
    is_available = interface.is_available()
    assert isinstance(is_available, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hardware_manager_get_best_device(sample_config):
    """Test getting best available device."""
    manager = HardwareManager(sample_config)
    await manager.initialize()

    device = manager.get_best_device()

    # Should return some device (CPU at minimum)
    assert device is not None

    await manager.shutdown()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hardware_manager_status(sample_config):
    """Test getting hardware status."""
    manager = HardwareManager(sample_config)
    await manager.initialize()

    status = manager.get_status()

    assert status is not None
    assert isinstance(status, dict)

    await manager.shutdown()


@pytest.mark.unit
def test_hardware_interface_mock(mock_hardware_interface):
    """Test mock hardware interface."""
    assert mock_hardware_interface.is_available() is True

    status = mock_hardware_interface.get_status()
    assert status["status"] == "ok"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hardware_fallback_to_cpu(sample_config):
    """Test fallback to CPU when no accelerator available."""
    sample_config.hardware.preferred = "hailo"
    sample_config.hardware.auto_detect = True

    manager = HardwareManager(sample_config)
    await manager.initialize()

    # Should fall back to CPU if Hailo not available
    device = manager.get_best_device()
    assert device is not None

    await manager.shutdown()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hardware_multiple_devices(sample_config):
    """Test managing multiple hardware devices."""
    sample_config.hardware.auto_detect = True
    manager = HardwareManager(sample_config)
    await manager.initialize()

    devices = manager.available_devices

    # Should have at least CPU
    assert len(devices) >= 1

    await manager.shutdown()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hardware_cleanup(sample_config):
    """Test hardware cleanup on shutdown."""
    manager = HardwareManager(sample_config)
    await manager.initialize()

    # Should cleanup without errors
    await manager.shutdown()

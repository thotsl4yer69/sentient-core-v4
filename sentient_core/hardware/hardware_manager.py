"""
Hardware Manager for automatic detection and management of AI accelerators.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base import HardwareInterface, HardwareType
from .hailo_interface import HailoInterface
from .coral_interface import CoralInterface

logger = logging.getLogger(__name__)


class HardwareManager:
    """
    Manages AI accelerator hardware detection and utilization.

    Automatically detects available hardware and provides intelligent
    model routing based on hardware capabilities.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize hardware manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.devices: Dict[str, HardwareInterface] = {}
        self.primary_device: Optional[HardwareInterface] = None
        self.detection_complete = False

    def detect_hardware(self) -> Dict[str, bool]:
        """
        Detect all available AI accelerators.

        Returns:
            Dictionary mapping hardware type to availability
        """
        logger.info("Detecting available AI accelerators...")

        detection_results = {}

        # Detect Hailo
        hailo = HailoInterface()
        if hailo.detect():
            detection_results['hailo'] = True
            self.devices['hailo'] = hailo
            logger.info("✓ Hailo AI Hat detected")
        else:
            detection_results['hailo'] = False
            logger.info("✗ Hailo AI Hat not found")

        # Detect Coral TPU
        coral = CoralInterface()
        if coral.detect():
            detection_results['coral'] = True
            self.devices['coral'] = coral
            logger.info("✓ Coral TPU detected")
        else:
            detection_results['coral'] = False
            logger.info("✗ Coral TPU not found")

        self.detection_complete = True

        # Set primary device
        if 'hailo' in self.devices:
            self.primary_device = self.devices['hailo']
            logger.info("Primary device: Hailo AI Hat")
        elif 'coral' in self.devices:
            self.primary_device = self.devices['coral']
            logger.info("Primary device: Coral TPU")
        else:
            logger.warning("No AI accelerators detected - CPU fallback")

        return detection_results

    def initialize_all(self) -> bool:
        """
        Initialize all detected hardware devices.

        Returns:
            True if at least one device initialized successfully
        """
        if not self.detection_complete:
            self.detect_hardware()

        success_count = 0

        for name, device in self.devices.items():
            try:
                if device.initialize():
                    logger.info(f"✓ Initialized {name}")
                    success_count += 1
                else:
                    logger.warning(f"✗ Failed to initialize {name}")
            except Exception as e:
                logger.error(f"Error initializing {name}: {e}")

        return success_count > 0

    def get_device(self, hardware_type: str) -> Optional[HardwareInterface]:
        """
        Get specific hardware device.

        Args:
            hardware_type: Type of hardware ('hailo', 'coral', etc.)

        Returns:
            Hardware interface or None
        """
        return self.devices.get(hardware_type)

    def load_model(self, model_path: str, hardware_type: Optional[str] = None, **kwargs) -> bool:
        """
        Load model onto specified or best available hardware.

        Args:
            model_path: Path to model file
            hardware_type: Specific hardware to use (optional)
            **kwargs: Additional loading parameters

        Returns:
            True if successful
        """
        model_path = Path(model_path)

        # Determine model type from extension
        model_ext = model_path.suffix.lower()

        # Auto-select hardware if not specified
        if hardware_type is None:
            if model_ext == '.hef':
                hardware_type = 'hailo'
            elif model_ext == '.tflite' or '_edgetpu' in model_path.stem:
                hardware_type = 'coral'
            elif self.primary_device:
                hardware_type = list(self.devices.keys())[0]
            else:
                logger.error("No hardware available for inference")
                return False

        # Get device
        device = self.devices.get(hardware_type)
        if not device:
            logger.error(f"Hardware not available: {hardware_type}")
            return False

        # Load model
        try:
            return device.load_model(str(model_path), **kwargs)
        except Exception as e:
            logger.error(f"Failed to load model on {hardware_type}: {e}")
            return False

    def infer(
        self,
        input_data: Any,
        hardware_type: Optional[str] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Run inference on specified or primary hardware.

        Args:
            input_data: Input tensor
            hardware_type: Hardware to use (optional, uses primary if None)
            **kwargs: Additional inference parameters

        Returns:
            Inference result or None
        """
        # Select device
        if hardware_type:
            device = self.devices.get(hardware_type)
        else:
            device = self.primary_device

        if not device:
            logger.error("No hardware available for inference")
            return None

        if not device.model_loaded:
            logger.error(f"{hardware_type or 'Primary'} device has no model loaded")
            return None

        # Run inference
        try:
            return device.infer(input_data, **kwargs)
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return None

    def get_all_info(self) -> Dict[str, Any]:
        """
        Get information about all hardware devices.

        Returns:
            Dictionary with hardware information
        """
        info = {
            'detection_complete': self.detection_complete,
            'devices_count': len(self.devices),
            'primary_device': self.primary_device.hardware_type.value if self.primary_device else None,
            'devices': {}
        }

        for name, device in self.devices.items():
            try:
                info['devices'][name] = device.get_info()
            except Exception as e:
                logger.error(f"Failed to get info for {name}: {e}")
                info['devices'][name] = {'error': str(e)}

        return info

    def cleanup_all(self):
        """Cleanup all hardware devices."""
        logger.info("Cleaning up all hardware devices...")

        for name, device in self.devices.items():
            try:
                device.cleanup()
                logger.info(f"✓ Cleaned up {name}")
            except Exception as e:
                logger.error(f"Error cleaning up {name}: {e}")

        self.devices.clear()
        self.primary_device = None
        self.detection_complete = False

    def get_hardware_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for all hardware.

        Returns:
            Dictionary with performance stats
        """
        stats = {}

        for name, device in self.devices.items():
            try:
                stats[name] = device.get_performance_stats()
            except Exception as e:
                logger.error(f"Failed to get stats for {name}: {e}")
                stats[name] = {'error': str(e)}

        return stats

    def __repr__(self) -> str:
        device_list = ', '.join(self.devices.keys()) if self.devices else 'none'
        return f"<HardwareManager(devices=[{device_list}], primary={self.primary_device.hardware_type.value if self.primary_device else None})>"

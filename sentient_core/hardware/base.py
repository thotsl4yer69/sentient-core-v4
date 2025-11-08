"""
Base hardware interface for AI accelerators.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List
import logging
import numpy as np

logger = logging.getLogger(__name__)


class HardwareType(Enum):
    """Hardware accelerator types."""
    CPU = "cpu"
    GPU = "gpu"
    HAILO = "hailo"
    CORAL = "coral"
    JETSON = "jetson"
    NPU = "npu"


class HardwareInterface(ABC):
    """
    Abstract base class for hardware accelerator interfaces.

    All hardware backends must implement this interface to provide
    unified inference capabilities across different accelerators.
    """

    def __init__(self, hardware_type: HardwareType, device_id: Optional[str] = None):
        """
        Initialize hardware interface.

        Args:
            hardware_type: Type of hardware accelerator
            device_id: Optional device identifier
        """
        self.hardware_type = hardware_type
        self.device_id = device_id or "0"
        self.initialized = False
        self.model_loaded = False
        self.current_model: Optional[str] = None

        logger.info(f"Created {hardware_type.value} interface (device: {self.device_id})")

    @abstractmethod
    def detect(self) -> bool:
        """
        Detect if hardware is available.

        Returns:
            True if hardware detected, False otherwise
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize hardware accelerator.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def load_model(self, model_path: str, **kwargs) -> bool:
        """
        Load model onto hardware.

        Args:
            model_path: Path to model file
            **kwargs: Additional model loading parameters

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def infer(self, input_data: np.ndarray, **kwargs) -> np.ndarray:
        """
        Run inference on hardware.

        Args:
            input_data: Input tensor
            **kwargs: Additional inference parameters

        Returns:
            Output tensor
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get hardware information.

        Returns:
            Dictionary with hardware details
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup and release hardware resources."""
        pass

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        return {
            'hardware_type': self.hardware_type.value,
            'device_id': self.device_id,
            'initialized': self.initialized,
            'model_loaded': self.model_loaded,
            'current_model': self.current_model
        }

    def validate_input(self, input_data: np.ndarray, expected_shape: Optional[tuple] = None) -> bool:
        """
        Validate input tensor.

        Args:
            input_data: Input tensor to validate
            expected_shape: Expected tensor shape (optional)

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(input_data, np.ndarray):
            logger.error(f"Input must be numpy array, got {type(input_data)}")
            return False

        if expected_shape and input_data.shape != expected_shape:
            logger.error(f"Shape mismatch: expected {expected_shape}, got {input_data.shape}")
            return False

        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(type={self.hardware_type.value}, device={self.device_id})>"

"""
Google Coral TPU Interface.

Supports Coral USB Accelerator and PCIe devices for edge AI inference.
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

from .base import HardwareInterface, HardwareType

logger = logging.getLogger(__name__)


class CoralInterface(HardwareInterface):
    """
    Interface for Google Coral Edge TPU.

    Provides optimized TensorFlow Lite inference on Edge TPU hardware.
    """

    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize Coral interface.

        Args:
            device_id: Coral device ID (default: first available)
        """
        super().__init__(HardwareType.CORAL, device_id)
        self.interpreter = None
        self.input_details = None
        self.output_details = None

    def detect(self) -> bool:
        """Detect Coral TPU availability."""
        try:
            from pycoral.utils import edgetpu

            devices = edgetpu.list_edge_tpus()

            if devices:
                logger.info(f"Detected Coral TPU devices: {len(devices)}")
                for i, dev in enumerate(devices):
                    logger.info(f"  Device {i}: {dev}")
                return True
            else:
                logger.warning("No Coral TPU devices found")
                return False

        except ImportError:
            logger.warning("PyCoral library not installed")
            return False
        except Exception as e:
            logger.error(f"Coral detection failed: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize Coral TPU."""
        if self.initialized:
            logger.warning("Coral already initialized")
            return True

        try:
            # Check if devices are available
            from pycoral.utils import edgetpu

            devices = edgetpu.list_edge_tpus()
            if not devices:
                logger.error("No Coral TPU devices found")
                return False

            logger.info(f"Coral TPU initialized (using device {self.device_id})")
            self.initialized = True
            return True

        except ImportError:
            logger.error("PyCoral library not available")
            return False
        except Exception as e:
            logger.error(f"Coral initialization failed: {e}")
            return False

    def load_model(self, model_path: str, **kwargs) -> bool:
        """
        Load TFLite model for Edge TPU.

        Args:
            model_path: Path to .tflite model file (must be EdgeTPU compiled)
            **kwargs: Additional loading parameters

        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            logger.error("Coral not initialized. Call initialize() first.")
            return False

        try:
            import tflite_runtime.interpreter as tflite
            from pycoral.utils import edgetpu

            # Create interpreter with Edge TPU delegate
            self.interpreter = tflite.Interpreter(
                model_path=model_path,
                experimental_delegates=[
                    tflite.load_delegate('libedgetpu.so.1', {'device': self.device_id})
                ]
            )

            # Allocate tensors
            self.interpreter.allocate_tensors()

            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            self.model_loaded = True
            self.current_model = model_path

            logger.info(f"Loaded Coral model: {model_path}")
            logger.info(f"  Inputs: {len(self.input_details)}")
            logger.info(f"  Outputs: {len(self.output_details)}")
            logger.info(f"  Input shape: {self.input_details[0]['shape']}")

            return True

        except ImportError as e:
            logger.error(f"Required libraries not available: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"Model file not found: {model_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to load Coral model: {e}")
            return False

    def infer(self, input_data: np.ndarray, **kwargs) -> np.ndarray:
        """
        Run inference on Coral TPU.

        Args:
            input_data: Input tensor (numpy array)
            **kwargs: Additional inference parameters

        Returns:
            Output tensor
        """
        if not self.model_loaded:
            raise RuntimeError("No model loaded. Call load_model() first.")

        try:
            from pycoral.adapters import common

            # Set input tensor
            common.set_input(self.interpreter, input_data)

            # Run inference
            self.interpreter.invoke()

            # Get output tensor
            output = common.output_tensor(self.interpreter, 0)

            return output

        except Exception as e:
            logger.error(f"Coral inference failed: {e}")
            raise

    def infer_classification(self, input_data: np.ndarray, top_k: int = 5) -> list:
        """
        Run classification inference with top-k results.

        Args:
            input_data: Input image tensor
            top_k: Number of top results to return

        Returns:
            List of (class_id, score) tuples
        """
        if not self.model_loaded:
            raise RuntimeError("No model loaded")

        try:
            from pycoral.adapters import classify, common

            # Set input
            common.set_input(self.interpreter, input_data)

            # Run inference
            self.interpreter.invoke()

            # Get classification results
            classes = classify.get_classes(self.interpreter, top_k=top_k)

            return [(c.id, c.score) for c in classes]

        except Exception as e:
            logger.error(f"Classification inference failed: {e}")
            raise

    def get_info(self) -> Dict[str, Any]:
        """Get Coral hardware information."""
        info = {
            'hardware_type': 'coral',
            'device_id': self.device_id,
            'initialized': self.initialized,
            'model_loaded': self.model_loaded,
            'current_model': self.current_model
        }

        try:
            from pycoral.utils import edgetpu

            devices = edgetpu.list_edge_tpus()
            info['available_devices'] = len(devices)
            info['device_info'] = [str(dev) for dev in devices]

        except Exception as e:
            logger.warning(f"Could not get device details: {e}")

        if self.input_details:
            info['model_info'] = {
                'input_shape': self.input_details[0]['shape'].tolist(),
                'input_dtype': str(self.input_details[0]['dtype']),
                'output_shape': self.output_details[0]['shape'].tolist(),
                'output_dtype': str(self.output_details[0]['dtype'])
            }

        return info

    def cleanup(self):
        """Cleanup Coral resources."""
        try:
            if self.interpreter:
                # TFLite interpreter doesn't need explicit cleanup
                self.interpreter = None

            self.input_details = None
            self.output_details = None
            self.model_loaded = False
            self.initialized = False

            logger.info("Coral cleanup complete")

        except Exception as e:
            logger.error(f"Error during Coral cleanup: {e}")

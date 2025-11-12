"""
Hailo AI Accelerator Interface for Raspberry Pi 5.

Supports Hailo-8 and Hailo-8L AI processors with 26 TOPS performance.
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

from .base import HardwareInterface, HardwareType

logger = logging.getLogger(__name__)


class HailoInterface(HardwareInterface):
    """
    Interface for Hailo AI Hat accelerator.

    Provides optimized inference for vision and neural network models
    on Raspberry Pi 5 with Hailo AI Hat.
    """

    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize Hailo interface.

        Args:
            device_id: Hailo device ID (default: first available)
        """
        super().__init__(HardwareType.HAILO, device_id)
        self.device = None
        self.network_group = None
        self.hef = None
        self.input_vstream_info = None
        self.output_vstream_info = None

    def detect(self) -> bool:
        """Detect Hailo hardware availability."""
        try:
            # Try importing Hailo platform
            import hailo_platform

            # Check for device files
            import os
            hailo_devices = [f for f in os.listdir('/dev') if f.startswith('hailo')]

            if hailo_devices:
                logger.info(f"Detected Hailo devices: {hailo_devices}")
                return True
            else:
                logger.warning("No Hailo devices found in /dev")
                return False

        except ImportError:
            logger.warning("Hailo platform library not installed")
            return False
        except FileNotFoundError:
            logger.warning("Cannot access /dev directory")
            return False
        except Exception as e:
            logger.error(f"Hailo detection failed: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize Hailo accelerator."""
        if self.initialized:
            logger.warning("Hailo already initialized")
            return True

        try:
            from hailo_platform import VDevice

            # Create virtual device
            self.device = VDevice()

            logger.info("Hailo device initialized successfully")
            self.initialized = True
            return True

        except ImportError:
            logger.error("Hailo platform library not available")
            return False
        except Exception as e:
            logger.error(f"Hailo initialization failed: {e}")
            return False

    def load_model(self, model_path: str, **kwargs) -> bool:
        """
        Load HEF model onto Hailo device.

        Args:
            model_path: Path to .hef model file
            **kwargs: Additional loading parameters

        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            logger.error("Hailo not initialized. Call initialize() first.")
            return False

        try:
            from hailo_platform import HEF, HailoStreamInterface, ConfigureParams

            # Load HEF file
            self.hef = HEF(model_path)

            # Configure network
            configure_params = ConfigureParams.create_from_hef(
                self.hef,
                interface=kwargs.get('interface', HailoStreamInterface.PCIe)
            )

            # Configure device with HEF
            network_groups = self.device.configure(self.hef, configure_params)
            self.network_group = network_groups[0]

            # Get input/output stream info
            self.input_vstream_info = self.hef.get_input_vstream_infos()
            self.output_vstream_info = self.hef.get_output_vstream_infos()

            self.model_loaded = True
            self.current_model = model_path

            logger.info(f"Loaded Hailo model: {model_path}")
            logger.info(f"  Inputs: {len(self.input_vstream_info)}")
            logger.info(f"  Outputs: {len(self.output_vstream_info)}")

            return True

        except ImportError:
            logger.error("Hailo platform library not available")
            return False
        except FileNotFoundError:
            logger.error(f"Model file not found: {model_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to load Hailo model: {e}")
            return False

    def infer(self, input_data: np.ndarray, **kwargs) -> np.ndarray:
        """
        Run inference on Hailo accelerator.

        Args:
            input_data: Input tensor (numpy array)
            **kwargs: Additional inference parameters

        Returns:
            Output tensor
        """
        if not self.model_loaded:
            raise RuntimeError("No model loaded. Call load_model() first.")

        try:
            from hailo_platform import InferVStreams

            # Prepare input dictionary
            if len(self.input_vstream_info) == 1:
                input_dict = {
                    self.input_vstream_info[0].name: input_data
                }
            else:
                # Multi-input model
                if isinstance(input_data, dict):
                    input_dict = input_data
                else:
                    raise ValueError("Multi-input model requires dict input")

            # Run inference
            with InferVStreams(self.network_group, input_dict) as infer_pipeline:
                results = infer_pipeline.infer(input_dict)

            # Extract output
            if len(self.output_vstream_info) == 1:
                output_name = self.output_vstream_info[0].name
                return results[output_name]
            else:
                # Return all outputs as dict
                return results

        except Exception as e:
            logger.error(f"Hailo inference failed: {e}")
            raise

    def get_info(self) -> Dict[str, Any]:
        """Get Hailo hardware information."""
        info = {
            'hardware_type': 'hailo',
            'device_id': self.device_id,
            'initialized': self.initialized,
            'model_loaded': self.model_loaded,
            'current_model': self.current_model
        }

        if self.device:
            try:
                # Get device info if available
                info['device_architecture'] = 'hailo-8'
                info['performance'] = '26 TOPS'
            except Exception as e:
                logger.warning(f"Could not get device details: {e}")

        if self.hef:
            info['model_info'] = {
                'inputs': len(self.input_vstream_info) if self.input_vstream_info else 0,
                'outputs': len(self.output_vstream_info) if self.output_vstream_info else 0
            }

        return info

    def get_firmware_version(self) -> Optional[str]:
        """Get Hailo firmware version."""
        if not self.initialized or not self.device:
            return None

        try:
            # Try to query firmware version from device
            # Different SDK versions may have different methods
            if hasattr(self.device, 'get_firmware_version'):
                return self.device.get_firmware_version()
            elif hasattr(self.device, 'firmware_version'):
                return self.device.firmware_version
            elif hasattr(self.device, 'info') and hasattr(self.device.info, 'firmware_version'):
                return self.device.info.firmware_version
            else:
                # Fallback if SDK doesn't provide firmware version method
                logger.debug("Firmware version query not supported by Hailo SDK")
                return "Unknown"
        except Exception as e:
            logger.error(f"Failed to get firmware version: {e}")
            return "Unknown"

    def cleanup(self):
        """Cleanup Hailo resources."""
        try:
            if self.network_group:
                self.network_group.release()
                self.network_group = None

            if self.device:
                self.device.release()
                self.device = None

            self.hef = None
            self.input_vstream_info = None
            self.output_vstream_info = None
            self.model_loaded = False
            self.initialized = False

            logger.info("Hailo cleanup complete")

        except Exception as e:
            logger.error(f"Error during Hailo cleanup: {e}")

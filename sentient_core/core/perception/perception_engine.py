"""
Perception engine for processing multi-modal inputs.
"""

import logging
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)


class PerceptionEngine:
    """
    Multi-modal perception engine.

    Processes various input modalities:
    - Text
    - Images
    - Audio
    - Sensor data
    """

    def __init__(self, config):
        """
        Initialize perception engine.

        Args:
            config: Configuration object
        """
        self.config = config

        # Modality settings
        self.text_enabled = config.get('perception.text.enabled', True)
        self.vision_enabled = config.get('perception.vision.enabled', False)
        self.audio_enabled = config.get('perception.audio.enabled', False)

        logger.info("PerceptionEngine created")

    def process(self, input_data: Any, modality: Optional[str] = None) -> Dict[str, Any]:
        """
        Process input data.

        Args:
            input_data: Input to process
            modality: Input modality (auto-detected if None)

        Returns:
            Processed perception data
        """
        # Auto-detect modality if not specified
        if modality is None:
            modality = self._detect_modality(input_data)

        logger.debug(f"Processing {modality} input")

        # Process based on modality
        if modality == 'text':
            return self._process_text(input_data)
        elif modality == 'image':
            return self._process_image(input_data)
        elif modality == 'audio':
            return self._process_audio(input_data)
        else:
            return self._process_generic(input_data)

    def _detect_modality(self, input_data: Any) -> str:
        """Auto-detect input modality."""
        import numpy as np

        if isinstance(input_data, str):
            return 'text'
        elif isinstance(input_data, dict):
            if 'text' in input_data:
                return 'text'
            elif 'image' in input_data:
                return 'image'
            elif 'audio' in input_data:
                return 'audio'
        elif isinstance(input_data, np.ndarray):
            if input_data.ndim == 3:  # Likely image
                return 'image'
            elif input_data.ndim == 1:  # Likely audio
                return 'audio'

        return 'unknown'

    def _process_text(self, text_data: Any) -> Dict[str, Any]:
        """Process text input."""
        if isinstance(text_data, dict):
            text = text_data.get('text', str(text_data))
        else:
            text = str(text_data)

        return {
            'modality': 'text',
            'text': text,
            'length': len(text),
            'processed': True
        }

    def _process_image(self, image_data: Any) -> Dict[str, Any]:
        """Process image input."""
        return {
            'modality': 'image',
            'data': image_data,
            'processed': True
        }

    def _process_audio(self, audio_data: Any) -> Dict[str, Any]:
        """Process audio input."""
        return {
            'modality': 'audio',
            'data': audio_data,
            'processed': True
        }

    def _process_generic(self, input_data: Any) -> Dict[str, Any]:
        """Process generic input."""
        return {
            'modality': 'generic',
            'data': input_data,
            'processed': True
        }

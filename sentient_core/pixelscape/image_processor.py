"""
Image processing utilities for Pixelscape.
"""

import logging
from typing import Dict, Any, Union, Tuple
import numpy as np
from pathlib import Path


logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Image preprocessing and manipulation utilities.
    """

    def __init__(self, config):
        """Initialize image processor."""
        self.config = config
        self.image_size = config.get('perception.vision.image_size', [224, 224])

    def process(self, image_data: Any) -> np.ndarray:
        """
        Process image data into standard format.

        Args:
            image_data: Image data (various formats)

        Returns:
            Processed image as numpy array
        """
        try:
            from PIL import Image

            # Handle different input types
            if isinstance(image_data, (str, Path)):
                image = Image.open(image_data)
            elif isinstance(image_data, np.ndarray):
                image = Image.fromarray(image_data.astype('uint8'))
            elif hasattr(image_data, 'convert'):  # PIL Image
                image = image_data
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize if needed
            if image.size != tuple(self.image_size):
                image = image.resize(tuple(self.image_size))

            # Convert to numpy array
            image_array = np.array(image)

            return image_array

        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise

    def get_properties(self, image: np.ndarray) -> Dict[str, Any]:
        """Get image properties."""
        return {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'min': float(image.min()),
            'max': float(image.max()),
            'mean': float(image.mean())
        }

    def resize(self, image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """Resize image."""
        from PIL import Image
        pil_image = Image.fromarray(image.astype('uint8'))
        resized = pil_image.resize(size)
        return np.array(resized)

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize image to [0, 1] range."""
        return image.astype(np.float32) / 255.0

    def augment(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Apply data augmentation."""
        # Basic augmentation (can be extended)
        augmented = image.copy()

        if kwargs.get('flip_horizontal'):
            augmented = np.fliplr(augmented)

        if kwargs.get('flip_vertical'):
            augmented = np.flipud(augmented)

        return augmented

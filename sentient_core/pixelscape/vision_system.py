"""
Pixelscape vision system for image and video processing.
"""

import logging
from typing import Dict, Any, Optional, Union, List
import numpy as np
from pathlib import Path

from .image_processor import ImageProcessor
from .scene_analyzer import SceneAnalyzer


logger = logging.getLogger(__name__)


class VisionSystem:
    """
    Pixelscape - Advanced vision processing system.

    Provides comprehensive visual understanding including:
    - Image classification and object detection
    - Scene understanding and segmentation
    - Visual question answering
    - Image generation and manipulation
    - Video processing
    """

    def __init__(self, config):
        """
        Initialize vision system.

        Args:
            config: Configuration object
        """
        self.config = config
        self.image_size = config.get('perception.vision.image_size', [224, 224])
        self.model_name = config.get('perception.vision.model', 'clip-vit-base')

        # Components
        self.image_processor: Optional[ImageProcessor] = None
        self.scene_analyzer: Optional[SceneAnalyzer] = None

        # Models
        self.vision_model = None
        self.clip_model = None
        self.clip_processor = None

        # State
        self.initialized = False

        logger.info("Pixelscape VisionSystem created")

    def initialize(self):
        """Initialize vision processing components."""
        if self.initialized:
            logger.warning("VisionSystem already initialized")
            return

        logger.info("Initializing Pixelscape vision system...")

        try:
            # Initialize image processor
            self.image_processor = ImageProcessor(self.config)

            # Initialize scene analyzer
            self.scene_analyzer = SceneAnalyzer(self.config)

            # Load vision models
            self._load_vision_models()

            self.initialized = True
            logger.info("Pixelscape vision system initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize vision system: {e}")
            logger.warning("Vision system will use fallback mode")

    def _load_vision_models(self):
        """Load vision models (CLIP, etc.)."""
        try:
            from transformers import CLIPModel, CLIPProcessor
            import torch

            logger.info(f"Loading vision model: {self.model_name}")

            # Load CLIP model for vision-language understanding
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

            # Set to eval mode
            self.clip_model.eval()

            logger.info("Vision models loaded successfully")

        except ImportError as e:
            logger.warning(f"Failed to load vision models: {e}")
            self.clip_model = None
            self.clip_processor = None

    def analyze(self, image_data: Any, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image and provide comprehensive understanding.

        Args:
            image_data: Image data (numpy array, PIL Image, or file path)
            prompt: Optional text prompt for guided analysis

        Returns:
            Analysis results dictionary
        """
        logger.info("Analyzing image with Pixelscape...")

        if not self.initialized:
            logger.warning("Vision system not initialized")
            return {'error': 'Vision system not initialized'}

        try:
            # Process image
            processed_image = self.image_processor.process(image_data)

            # Perform scene analysis
            scene_info = self.scene_analyzer.analyze(processed_image)

            # Vision-language analysis if prompt provided
            vl_results = None
            if prompt and self.clip_model:
                vl_results = self._vision_language_analysis(processed_image, prompt)

            # Combine results
            analysis = {
                'scene': scene_info,
                'vision_language': vl_results,
                'image_properties': self.image_processor.get_properties(processed_image),
                'status': 'completed'
            }

            return analysis

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {'error': str(e), 'status': 'failed'}

    def _vision_language_analysis(self, image: Any, text: str) -> Dict[str, Any]:
        """
        Perform vision-language analysis using CLIP.

        Args:
            image: Processed image
            text: Text prompt or query

        Returns:
            Analysis results
        """
        try:
            import torch
            from PIL import Image

            # Convert to PIL if needed
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image.astype('uint8'))

            # Process inputs
            inputs = self.clip_processor(
                text=[text],
                images=image,
                return_tensors="pt",
                padding=True
            )

            # Get features
            with torch.no_grad():
                outputs = self.clip_model(**inputs)

            # Calculate similarity
            logits_per_image = outputs.logits_per_image
            similarity = logits_per_image.softmax(dim=1)[0].item()

            return {
                'prompt': text,
                'similarity': float(similarity),
                'confidence': float(similarity)
            }

        except Exception as e:
            logger.error(f"Vision-language analysis failed: {e}")
            return {'error': str(e)}

    def detect_objects(self, image_data: Any) -> List[Dict[str, Any]]:
        """
        Detect objects in an image.

        Args:
            image_data: Image data

        Returns:
            List of detected objects with bounding boxes
        """
        logger.info("Detecting objects...")

        if not self.initialized:
            return []

        try:
            processed_image = self.image_processor.process(image_data)
            objects = self.scene_analyzer.detect_objects(processed_image)
            return objects

        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []

    def classify_image(self, image_data: Any, labels: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Classify an image into categories.

        Args:
            image_data: Image data
            labels: Optional list of labels to classify against

        Returns:
            Dictionary of label probabilities
        """
        logger.info("Classifying image...")

        if not self.initialized or not self.clip_model:
            return {}

        try:
            from PIL import Image
            import torch

            # Process image
            processed_image = self.image_processor.process(image_data)

            if isinstance(processed_image, np.ndarray):
                processed_image = Image.fromarray(processed_image.astype('uint8'))

            # Default labels if not provided
            if not labels:
                labels = [
                    "a photo of a person",
                    "a photo of an animal",
                    "a photo of a landscape",
                    "a photo of an object",
                    "a photo of food",
                    "a photo of a building"
                ]

            # Process inputs
            inputs = self.clip_processor(
                text=labels,
                images=processed_image,
                return_tensors="pt",
                padding=True
            )

            # Get predictions
            with torch.no_grad():
                outputs = self.clip_model(**inputs)

            # Get probabilities
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)[0]

            # Create results dictionary
            results = {label: float(prob) for label, prob in zip(labels, probs)}

            return results

        except Exception as e:
            logger.error(f"Image classification failed: {e}")
            return {}

    def segment_image(self, image_data: Any) -> Dict[str, Any]:
        """
        Perform semantic segmentation on an image.

        Args:
            image_data: Image data

        Returns:
            Segmentation results
        """
        logger.info("Segmenting image...")

        if not self.initialized:
            return {'error': 'Vision system not initialized'}

        try:
            processed_image = self.image_processor.process(image_data)
            segmentation = self.scene_analyzer.segment(processed_image)
            return segmentation

        except Exception as e:
            logger.error(f"Image segmentation failed: {e}")
            return {'error': str(e)}

    def process_video(self, video_path: str, sample_rate: int = 1) -> List[Dict[str, Any]]:
        """
        Process video and analyze frames.

        Args:
            video_path: Path to video file
            sample_rate: Process every N frames

        Returns:
            List of frame analysis results
        """
        logger.info(f"Processing video: {video_path}")

        if not self.initialized:
            return []

        try:
            import cv2

            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            results = []

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % sample_rate == 0:
                    # Analyze frame
                    analysis = self.analyze(frame)
                    analysis['frame_number'] = frame_count
                    results.append(analysis)

                frame_count += 1

            cap.release()

            logger.info(f"Processed {len(results)} frames from video")
            return results

        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            return []

    def get_info(self) -> Dict[str, Any]:
        """Get vision system information."""
        return {
            'initialized': self.initialized,
            'model': self.model_name,
            'image_size': self.image_size,
            'clip_available': self.clip_model is not None,
            'components': {
                'image_processor': self.image_processor is not None,
                'scene_analyzer': self.scene_analyzer is not None
            }
        }

    def shutdown(self):
        """Shutdown vision system."""
        logger.info("Shutting down Pixelscape vision system...")

        if self.clip_model:
            del self.clip_model
            self.clip_model = None

        if self.clip_processor:
            del self.clip_processor
            self.clip_processor = None

        self.initialized = False

        logger.info("Vision system shutdown complete")

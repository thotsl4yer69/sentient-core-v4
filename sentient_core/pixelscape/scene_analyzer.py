"""
Scene analysis and understanding for Pixelscape.
"""

import logging
from typing import Dict, Any, List
import numpy as np


logger = logging.getLogger(__name__)


class SceneAnalyzer:
    """
    Analyzes scenes and understands visual context.
    """

    def __init__(self, config):
        """Initialize scene analyzer."""
        self.config = config
        self.detection_model = None
        self.segmentation_model = None

    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze scene from image.

        Args:
            image: Processed image array

        Returns:
            Scene analysis results
        """
        try:
            # Basic scene analysis
            analysis = {
                'brightness': self._calculate_brightness(image),
                'contrast': self._calculate_contrast(image),
                'dominant_colors': self._extract_dominant_colors(image),
                'complexity': self._estimate_complexity(image)
            }

            return analysis

        except Exception as e:
            logger.error(f"Scene analysis failed: {e}")
            return {'error': str(e)}

    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect objects in the image using YOLOv8.

        Args:
            image: Image array

        Returns:
            List of detected objects with bounding boxes, confidence, and labels
        """
        try:
            # Lazy load YOLO model
            if self.detection_model is None:
                self._load_detection_model()

            if self.detection_model is None:
                logger.warning("Detection model not available, using fallback")
                return []

            from PIL import Image
            import torch

            # Convert to PIL Image
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image.astype('uint8'))
            else:
                pil_image = image

            # Run inference
            with torch.no_grad():
                results = self.detection_model(pil_image)

            # Parse results
            detections = []

            # Handle different YOLO result formats
            if hasattr(results, 'pandas'):
                # YOLOv5/v8 format
                df = results.pandas().xyxy[0]
                for _, row in df.iterrows():
                    detections.append({
                        'label': row['name'],
                        'confidence': float(row['confidence']),
                        'bbox': [
                            float(row['xmin']),
                            float(row['ymin']),
                            float(row['xmax']),
                            float(row['ymax'])
                        ]
                    })
            elif isinstance(results, list):
                # Ultralytics YOLO format
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        detections.append({
                            'label': result.names[int(box.cls)],
                            'confidence': float(box.conf),
                            'bbox': box.xyxy[0].tolist()
                        })

            logger.info(f"Detected {len(detections)} objects")
            return detections

        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []

    def _load_detection_model(self):
        """Load object detection model (YOLOv8)."""
        try:
            # Try loading YOLOv8 from ultralytics
            from ultralytics import YOLO
            from sentient_core.models.model_downloader import ensure_model

            logger.info("Loading YOLOv8 detection model...")

            # Ensure model is downloaded
            model_path = ensure_model("yolov8n")

            # Load model
            self.detection_model = YOLO(str(model_path))

            logger.info("YOLOv8 detection model loaded")

        except ImportError:
            logger.warning("ultralytics package not available")
            self.detection_model = None
        except Exception as e:
            logger.error(f"Failed to load detection model: {e}")
            self.detection_model = None

    def segment(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Perform semantic segmentation using simple algorithms.

        Args:
            image: Image array

        Returns:
            Segmentation results with segments and mask
        """
        try:
            # Lazy load segmentation model
            if self.segmentation_model is None:
                self._load_segmentation_model()

            if self.segmentation_model is None:
                # Fallback to simple segmentation
                return self._simple_segmentation(image)

            from PIL import Image
            import torch

            # Convert to PIL
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image.astype('uint8'))
            else:
                pil_image = image

            # Run segmentation
            with torch.no_grad():
                results = self.segmentation_model(pil_image)

            # Parse results
            segments = []
            mask = None

            if hasattr(results, 'masks') and results.masks is not None:
                masks = results.masks.data
                mask = masks[0].cpu().numpy() if len(masks) > 0 else None

                for i, m in enumerate(masks):
                    segments.append({
                        'segment_id': i,
                        'mask': m.cpu().numpy().tolist()
                    })

            return {
                'segments': segments,
                'mask': mask.tolist() if mask is not None else None,
                'num_segments': len(segments)
            }

        except Exception as e:
            logger.error(f"Semantic segmentation failed: {e}")
            return self._simple_segmentation(image)

    def _load_segmentation_model(self):
        """Load segmentation model."""
        try:
            from ultralytics import YOLO

            logger.info("Loading segmentation model...")

            # Use YOLOv8 segmentation model
            # Note: This would need a proper segmentation model
            # For now, set to None to use fallback
            self.segmentation_model = None

            logger.info("Segmentation model status: fallback mode")

        except Exception as e:
            logger.error(f"Failed to load segmentation model: {e}")
            self.segmentation_model = None

    def _simple_segmentation(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Simple color-based segmentation fallback.

        Args:
            image: Image array

        Returns:
            Basic segmentation results
        """
        try:
            from sklearn.cluster import KMeans

            # Reshape image
            h, w, c = image.shape
            pixels = image.reshape(-1, 3)

            # Perform k-means clustering
            n_segments = 5
            kmeans = KMeans(n_clusters=n_segments, random_state=42, n_init=10)
            labels = kmeans.fit_predict(pixels)

            # Reshape back to image
            mask = labels.reshape(h, w)

            # Create segments
            segments = []
            for i in range(n_segments):
                segment_mask = (mask == i).astype(int)
                segments.append({
                    'segment_id': i,
                    'color': kmeans.cluster_centers_[i].astype(int).tolist(),
                    'pixel_count': int(np.sum(segment_mask))
                })

            return {
                'segments': segments,
                'mask': mask.tolist(),
                'num_segments': n_segments,
                'method': 'kmeans_color'
            }

        except Exception as e:
            logger.error(f"Simple segmentation failed: {e}")
            return {
                'segments': [],
                'mask': None,
                'error': str(e)
            }

    def _calculate_brightness(self, image: np.ndarray) -> float:
        """Calculate average brightness."""
        gray = np.mean(image, axis=2)
        return float(np.mean(gray))

    def _calculate_contrast(self, image: np.ndarray) -> float:
        """Calculate image contrast."""
        gray = np.mean(image, axis=2)
        return float(np.std(gray))

    def _extract_dominant_colors(self, image: np.ndarray, n_colors: int = 5) -> List[List[int]]:
        """Extract dominant colors from image."""
        # Reshape image to be a list of pixels
        pixels = image.reshape(-1, 3)

        # Simple color extraction using k-means (if sklearn available)
        try:
            from sklearn.cluster import KMeans

            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)

            colors = kmeans.cluster_centers_.astype(int)
            return colors.tolist()

        except ImportError:
            # Fallback: return mean color
            mean_color = np.mean(pixels, axis=0).astype(int)
            return [mean_color.tolist()]

    def _estimate_complexity(self, image: np.ndarray) -> float:
        """Estimate scene complexity."""
        # Use gradient magnitude as proxy for complexity
        try:
            gray = np.mean(image, axis=2)

            # Calculate gradients
            gx = np.gradient(gray, axis=0)
            gy = np.gradient(gray, axis=1)

            # Gradient magnitude
            gradient_magnitude = np.sqrt(gx**2 + gy**2)

            # Normalize and return mean
            complexity = np.mean(gradient_magnitude) / 255.0

            return float(complexity)

        except Exception as e:
            logger.error(f"Complexity estimation failed: {e}")
            return 0.0

"""
Multi-Sensor Data Fusion System.

Combines data from multiple sensors for unified perception.
"""

import threading
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class SensorFusion:
    """
    Fuses data from multiple sensors into cohesive world model.

    Combines:
    - Vision data
    - RF signals
    - Audio
    - Environmental sensors
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize sensor fusion.

        Args:
            config: Configuration object
        """
        self.config = config or {}
        self.running = False
        self.fusion_thread: Optional[threading.Thread] = None

        # Sensor data storage
        self.sensor_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.fused_state: Dict[str, Any] = {}

        # Thread safety
        self.lock = threading.Lock()

        # Fusion parameters
        self.fusion_rate = self.config.get('fusion_rate', 20)  # Hz
        self.max_history = self.config.get('max_sensor_history', 100)

        logger.info("Sensor Fusion initialized")

    def start(self):
        """Start sensor fusion loop."""
        if self.running:
            logger.warning("Sensor Fusion already running")
            return

        self.running = True
        self.fusion_thread = threading.Thread(target=self._fusion_loop, daemon=True)
        self.fusion_thread.start()

        logger.info("Sensor Fusion started")

    def _fusion_loop(self):
        """Main fusion loop."""
        fusion_interval = 1.0 / self.fusion_rate

        while self.running:
            try:
                # Fuse all sensor data
                self._fuse_sensors()

                time.sleep(fusion_interval)

            except Exception as e:
                logger.error(f"Sensor fusion error: {e}")
                time.sleep(1)

    def _fuse_sensors(self):
        """Fuse data from all sensors."""
        with self.lock:
            # Temporal alignment of sensor data
            aligned_data = self._temporal_alignment()

            # Spatial fusion (if applicable)
            spatial_data = self._spatial_fusion(aligned_data)

            # Semantic fusion
            semantic_data = self._semantic_fusion(spatial_data)

            # Update fused state
            self.fused_state = {
                'timestamp': datetime.now().isoformat(),
                'sensors_active': list(self.sensor_data.keys()),
                'fused_perception': semantic_data,
                'confidence': self._compute_confidence()
            }

    def _temporal_alignment(self) -> Dict[str, Any]:
        """Align sensor data temporally."""
        # Get most recent data from each sensor
        aligned = {}

        for sensor_id, data_list in self.sensor_data.items():
            if data_list:
                # Get most recent entry
                aligned[sensor_id] = data_list[-1]

        return aligned

    def _spatial_fusion(self, aligned_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fuse spatially-related sensor data."""
        # Combine spatial information from different sensors
        spatial = {
            'objects_detected': [],
            'environment': {},
            'threats': []
        }

        # Process vision data
        if 'vision' in aligned_data:
            vision = aligned_data['vision']
            spatial['objects_detected'].extend(vision.get('objects', []))

        # Process RF data
        if 'rf' in aligned_data:
            rf = aligned_data['rf']
            spatial['threats'].extend(rf.get('detections', []))

        return spatial

    def _semantic_fusion(self, spatial_data: Dict[str, Any]) -> Dict[str, Any]:
        """High-level semantic fusion."""
        semantic = {
            'scene_understanding': 'unknown',
            'threat_level': 0.0,
            'entities': []
        }

        # Assess threat level
        if spatial_data.get('threats'):
            semantic['threat_level'] = min(1.0, len(spatial_data['threats']) * 0.3)

        # Count entities
        semantic['entities'] = spatial_data.get('objects_detected', [])

        return semantic

    def _compute_confidence(self) -> float:
        """Compute overall fusion confidence."""
        with self.lock:
            if not self.sensor_data:
                return 0.0

            # Base confidence on number of active sensors
            active_sensors = len([
                s for s in self.sensor_data.values()
                if s and (datetime.now() - datetime.fromisoformat(s[-1].get('timestamp', datetime.now().isoformat()))).total_seconds() < 5
            ])

            return min(1.0, active_sensors * 0.25)

    def update_sensor(self, sensor_id: str, data: Dict[str, Any]):
        """
        Update data from a sensor.

        Args:
            sensor_id: Sensor identifier
            data: Sensor data dictionary
        """
        with self.lock:
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()

            # Add to sensor data
            self.sensor_data[sensor_id].append(data)

            # Limit history size
            if len(self.sensor_data[sensor_id]) > self.max_history:
                self.sensor_data[sensor_id] = self.sensor_data[sensor_id][-self.max_history:]

    def get_fused_state(self) -> Dict[str, Any]:
        """
        Get current fused sensor state.

        Returns:
            Fused state dictionary
        """
        with self.lock:
            return self.fused_state.copy()

    def get_sensor_data(self, sensor_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent data from specific sensor.

        Args:
            sensor_id: Sensor identifier
            limit: Maximum number of entries to return

        Returns:
            List of sensor data entries
        """
        with self.lock:
            return self.sensor_data[sensor_id][-limit:] if sensor_id in self.sensor_data else []

    def stop(self):
        """Stop sensor fusion."""
        self.running = False

        if self.fusion_thread:
            self.fusion_thread.join(timeout=2)

        logger.info("Sensor Fusion stopped")

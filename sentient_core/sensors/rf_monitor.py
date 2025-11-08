"""
RF Signal Monitoring and Drone Detection System.

Monitors radio frequency spectrum for:
- Drone control signals (2.4 GHz, 5.8 GHz)
- Unknown RF emissions
- Signal pattern analysis
"""

import threading
import logging
import time
import queue
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class RFMonitor:
    """
    RF signal monitoring system.

    Captures and analyzes RF spectrum data for anomaly detection
    and signal identification.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize RF monitor.

        Args:
            config: Configuration object
        """
        self.config = config or {}
        self.running = False
        self.detection_queue = queue.Queue()
        self.monitor_thread: Optional[threading.Thread] = None

        # RF parameters
        self.sample_rate = self.config.get('rf_sample_rate', 2.4e6)  # 2.4 MHz
        self.center_frequency = self.config.get('rf_center_freq', 2.4e9)  # 2.4 GHz
        self.gain = self.config.get('rf_gain', 30)

        # SDR device
        self.sdr = None
        self.sdr_available = False

        logger.info("RF Monitor initialized")

    def detect_sdr(self) -> bool:
        """
        Detect if SDR hardware is available.

        Returns:
            True if SDR detected
        """
        try:
            # Try RTL-SDR first
            from rtlsdr import RtlSdr

            self.sdr = RtlSdr()
            self.sdr_available = True
            logger.info("RTL-SDR detected")
            return True

        except ImportError:
            logger.warning("RTL-SDR library not installed")
            return False
        except Exception as e:
            logger.warning(f"No RTL-SDR hardware detected: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize SDR hardware."""
        if not self.detect_sdr():
            logger.warning("No SDR hardware available - running in simulation mode")
            self.sdr_available = False
            return True  # Allow to run in simulation mode

        try:
            # Configure SDR
            self.sdr.sample_rate = self.sample_rate
            self.sdr.center_freq = self.center_frequency
            self.sdr.gain = self.gain

            logger.info(f"SDR configured: {self.sample_rate/1e6} MHz @ {self.center_frequency/1e9} GHz")
            return True

        except Exception as e:
            logger.error(f"SDR initialization failed: {e}")
            return False

    def start(self):
        """Start RF monitoring."""
        if self.running:
            logger.warning("RF Monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("RF Monitor started")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                if self.sdr_available:
                    # Capture real RF samples
                    samples = self.sdr.read_samples(256 * 1024)
                    self._process_samples(samples)
                else:
                    # Simulation mode
                    time.sleep(0.1)
                    self._simulate_monitoring()

            except Exception as e:
                logger.error(f"RF monitoring error: {e}")
                time.sleep(1)

    def _process_samples(self, samples: np.ndarray):
        """
        Process RF samples for signal detection.

        Args:
            samples: Complex IQ samples
        """
        try:
            # Compute power spectral density
            psd = np.abs(np.fft.fftshift(np.fft.fft(samples))) ** 2

            # Detect peaks
            threshold = np.mean(psd) + 3 * np.std(psd)
            peaks = psd > threshold

            if np.any(peaks):
                # Signal detected
                peak_indices = np.where(peaks)[0]
                for peak_idx in peak_indices:
                    freq_offset = (peak_idx - len(psd) // 2) * (self.sample_rate / len(psd))
                    actual_freq = self.center_frequency + freq_offset

                    detection = {
                        'type': 'rf_signal',
                        'frequency': actual_freq,
                        'power': float(psd[peak_idx]),
                        'timestamp': datetime.now().isoformat()
                    }

                    self.detection_queue.put(detection)
                    logger.debug(f"RF signal detected at {actual_freq/1e9:.3f} GHz")

        except Exception as e:
            logger.error(f"Sample processing error: {e}")

    def _simulate_monitoring(self):
        """Simulate RF monitoring for testing."""
        # Randomly generate simulated detections
        import random

        if random.random() < 0.01:  # 1% chance per iteration
            detection = {
                'type': 'rf_signal_simulated',
                'frequency': random.uniform(2.4e9, 2.5e9),
                'power': random.uniform(50, 100),
                'timestamp': datetime.now().isoformat()
            }
            self.detection_queue.put(detection)

    def get_detections(self) -> List[Dict[str, Any]]:
        """
        Get all pending detections.

        Returns:
            List of detection dictionaries
        """
        detections = []
        while not self.detection_queue.empty():
            try:
                detections.append(self.detection_queue.get_nowait())
            except queue.Empty:
                break
        return detections

    def stop(self):
        """Stop RF monitoring."""
        self.running = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        if self.sdr:
            self.sdr.close()

        logger.info("RF Monitor stopped")

    def __del__(self):
        """Cleanup on deletion."""
        if self.sdr:
            try:
                self.sdr.close()
            except:
                pass


class DroneDetector:
    """
    Drone detection system using RF signatures.

    Identifies drone control signals and telemetry.
    """

    def __init__(self, rf_monitor: RFMonitor):
        """
        Initialize drone detector.

        Args:
            rf_monitor: RFMonitor instance
        """
        self.rf_monitor = rf_monitor
        self.drone_signatures = self._load_drone_signatures()
        self.detected_drones: List[Dict[str, Any]] = []

    def _load_drone_signatures(self) -> Dict[str, Dict[str, Any]]:
        """
        Load known drone RF signatures.

        Returns:
            Dictionary of drone signatures
        """
        # Common drone frequencies
        signatures = {
            'dji_phantom': {
                'control_freq': 2.4e9,
                'video_freq': 5.8e9,
                'bandwidth': 20e6,
                'modulation': 'FHSS'
            },
            'dji_mavic': {
                'control_freq': 2.4e9,
                'video_freq': 5.8e9,
                'bandwidth': 20e6,
                'modulation': 'OFDM'
            },
            'generic_2.4ghz': {
                'control_freq': 2.4e9,
                'bandwidth': 1e6,
                'modulation': 'Unknown'
            },
            'generic_5.8ghz': {
                'control_freq': 5.8e9,
                'bandwidth': 10e6,
                'modulation': 'Unknown'
            }
        }
        return signatures

    def analyze_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze RF detections for drone signatures.

        Args:
            detections: List of RF detections

        Returns:
            List of identified drones
        """
        identified_drones = []

        for detection in detections:
            freq = detection.get('frequency', 0)

            # Check against known signatures
            for drone_type, signature in self.drone_signatures.items():
                control_freq = signature['control_freq']
                bandwidth = signature.get('bandwidth', 10e6)

                # Check if frequency matches (within bandwidth)
                if abs(freq - control_freq) < bandwidth / 2:
                    drone_detection = {
                        'type': 'drone',
                        'drone_type': drone_type,
                        'confidence': 0.7,  # Base confidence
                        'frequency': freq,
                        'power': detection.get('power', 0),
                        'timestamp': detection.get('timestamp'),
                        'signature_match': signature
                    }

                    identified_drones.append(drone_detection)
                    logger.info(f"Potential {drone_type} detected at {freq/1e9:.3f} GHz")

        return identified_drones

    def get_active_drones(self) -> List[Dict[str, Any]]:
        """
        Get currently active drone detections.

        Returns:
            List of active drones
        """
        # Get recent detections from RF monitor
        detections = self.rf_monitor.get_detections()

        # Analyze for drones
        drones = self.analyze_detections(detections)

        # Update detected drones list
        self.detected_drones.extend(drones)

        # Keep only recent detections (last minute)
        now = datetime.now()
        self.detected_drones = [
            d for d in self.detected_drones
            if (now - datetime.fromisoformat(d['timestamp'])).total_seconds() < 60
        ]

        return self.detected_drones

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get drone detection statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'total_detections': len(self.detected_drones),
            'unique_types': len(set(d['drone_type'] for d in self.detected_drones)),
            'active_count': len(self.get_active_drones())
        }

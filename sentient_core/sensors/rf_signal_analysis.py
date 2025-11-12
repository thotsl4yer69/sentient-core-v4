"""
Advanced RF signal analysis and pattern recognition.

Provides sophisticated signal processing capabilities for:
- Drone detection and classification
- Signal pattern matching
- Modulation analysis
- Spectral analysis
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from scipy import signal as scipy_signal
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class SignalPattern:
    """Represents a known RF signal pattern."""
    name: str
    frequency_range: Tuple[float, float]  # Hz
    bandwidth: float  # Hz
    modulation_type: str
    characteristics: Dict[str, Any]


# Known drone signal patterns
DRONE_PATTERNS = [
    SignalPattern(
        name="DJI Phantom",
        frequency_range=(2.400e9, 2.483e9),
        bandwidth=20e6,
        modulation_type="OFDM",
        characteristics={
            "hop_rate": 100,  # Hz
            "channel_count": 40,
            "typical_power": -40,  # dBm
        }
    ),
    SignalPattern(
        name="DJI Mavic",
        frequency_range=(5.725e9, 5.850e9),
        bandwidth=10e6,
        modulation_type="OFDM",
        characteristics={
            "hop_rate": 200,
            "channel_count": 8,
            "typical_power": -35,
        }
    ),
    SignalPattern(
        name="FPV Drone (5.8GHz)",
        frequency_range=(5.645e9, 5.945e9),
        bandwidth=40e6,
        modulation_type="Analog FM",
        characteristics={
            "typical_power": -30,
            "video_signal": True,
        }
    ),
]


class RFSignalAnalyzer:
    """
    Advanced RF signal analysis engine.

    Provides sophisticated signal processing and pattern recognition.
    """

    def __init__(self, sample_rate: float = 2.4e6):
        """
        Initialize signal analyzer.

        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.known_patterns = DRONE_PATTERNS.copy()

        # Signal history for tracking
        self.signal_history = deque(maxlen=100)

        logger.info(f"RF Signal Analyzer initialized (SR: {sample_rate/1e6:.1f} MHz)")

    def analyze_spectrum(self, samples: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive spectral analysis of RF samples.

        Args:
            samples: Complex IQ samples

        Returns:
            Analysis results dictionary
        """
        try:
            # Compute FFT
            fft_result = np.fft.fftshift(np.fft.fft(samples))
            frequencies = np.fft.fftshift(np.fft.fftfreq(len(samples), 1/self.sample_rate))

            # Power spectral density
            psd = 10 * np.log10(np.abs(fft_result) ** 2 + 1e-10)

            # Find peaks
            peaks, properties = scipy_signal.find_peaks(
                psd,
                height=np.mean(psd) + 2 * np.std(psd),
                distance=10
            )

            # Analyze peaks
            detected_signals = []
            for peak_idx in peaks:
                signal_info = {
                    'frequency': float(frequencies[peak_idx]),
                    'power_dbm': float(psd[peak_idx]),
                    'bandwidth': self._estimate_bandwidth(psd, peak_idx),
                }
                detected_signals.append(signal_info)

            # Overall statistics
            analysis = {
                'peak_signals': detected_signals,
                'num_signals': len(detected_signals),
                'mean_power': float(np.mean(psd)),
                'max_power': float(np.max(psd)),
                'snr_estimate': float(np.max(psd) - np.mean(psd)),
                'spectrum': psd.tolist() if len(psd) <= 1024 else psd[::len(psd)//1024].tolist(),
                'frequencies': frequencies.tolist() if len(frequencies) <= 1024 else frequencies[::len(frequencies)//1024].tolist(),
            }

            return analysis

        except Exception as e:
            logger.error(f"Spectrum analysis failed: {e}")
            return {'error': str(e)}

    def _estimate_bandwidth(self, psd: np.ndarray, peak_idx: int, threshold_db: float = 3) -> float:
        """
        Estimate signal bandwidth around a peak.

        Args:
            psd: Power spectral density array
            peak_idx: Index of peak
            threshold_db: dB below peak to measure bandwidth

        Returns:
            Estimated bandwidth in Hz
        """
        peak_power = psd[peak_idx]
        threshold = peak_power - threshold_db

        # Find left edge
        left_idx = peak_idx
        while left_idx > 0 and psd[left_idx] > threshold:
            left_idx -= 1

        # Find right edge
        right_idx = peak_idx
        while right_idx < len(psd) - 1 and psd[right_idx] > threshold:
            right_idx += 1

        # Calculate bandwidth
        bandwidth = (right_idx - left_idx) * (self.sample_rate / len(psd))

        return float(bandwidth)

    def detect_modulation(self, samples: np.ndarray) -> str:
        """
        Attempt to identify signal modulation type.

        Args:
            samples: Complex IQ samples

        Returns:
            Estimated modulation type
        """
        try:
            # Instantaneous phase
            phase = np.unwrap(np.angle(samples))
            phase_diff = np.diff(phase)

            # Instantaneous frequency
            inst_freq = phase_diff / (2 * np.pi)

            # Check for FM characteristics
            fm_variance = np.var(inst_freq)

            # Check for AM characteristics
            amplitude = np.abs(samples)
            am_variance = np.var(amplitude)

            # Simple classification
            if fm_variance > am_variance * 2:
                return "FM"
            elif am_variance > fm_variance * 2:
                return "AM"
            else:
                # Check for digital modulation
                if self._check_digital_modulation(samples):
                    return "Digital (PSK/QAM/OFDM)"
                else:
                    return "Unknown"

        except Exception as e:
            logger.error(f"Modulation detection failed: {e}")
            return "Unknown"

    def _check_digital_modulation(self, samples: np.ndarray) -> bool:
        """
        Check if signal appears to be digitally modulated.

        Args:
            samples: Complex IQ samples

        Returns:
            True if appears to be digital modulation
        """
        try:
            # Constellation analysis
            # Digital signals tend to cluster at specific points
            amplitude = np.abs(samples)
            phase = np.angle(samples)

            # Check for clustering in phase
            phase_hist, _ = np.histogram(phase, bins=16)
            phase_entropy = -np.sum((phase_hist / np.sum(phase_hist)) * np.log2(phase_hist / np.sum(phase_hist) + 1e-10))

            # Lower entropy suggests clustering (digital modulation)
            return phase_entropy < 3.0

        except:
            return False

    def match_pattern(self, signal_info: Dict[str, Any]) -> Optional[SignalPattern]:
        """
        Match detected signal against known patterns.

        Args:
            signal_info: Signal information dict

        Returns:
            Matched pattern or None
        """
        frequency = signal_info.get('frequency', 0)
        bandwidth = signal_info.get('bandwidth', 0)

        for pattern in self.known_patterns:
            # Check frequency range
            if pattern.frequency_range[0] <= frequency <= pattern.frequency_range[1]:
                # Check bandwidth match (within 50%)
                if bandwidth > 0:
                    bw_ratio = bandwidth / pattern.bandwidth
                    if 0.5 <= bw_ratio <= 2.0:
                        return pattern

        return None

    def track_signals(self, detections: List[Dict[str, Any]]):
        """
        Track signals over time for pattern analysis.

        Args:
            detections: List of signal detections
        """
        self.signal_history.append({
            'timestamp': time.time(),
            'detections': detections
        })

    def get_signal_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on tracked signals.

        Returns:
            Statistics dictionary
        """
        if not self.signal_history:
            return {'total_detections': 0}

        total_detections = sum(len(h['detections']) for h in self.signal_history)

        # Frequency histogram
        all_frequencies = []
        for history in self.signal_history:
            for detection in history['detections']:
                if 'frequency' in detection:
                    all_frequencies.append(detection['frequency'])

        stats = {
            'total_detections': total_detections,
            'history_length': len(self.signal_history),
            'avg_detections_per_scan': total_detections / len(self.signal_history) if self.signal_history else 0,
        }

        if all_frequencies:
            stats['frequency_range'] = [min(all_frequencies), max(all_frequencies)]
            stats['most_common_frequency'] = float(np.median(all_frequencies))

        return stats


class DroneSignatureDetector:
    """
    Specialized detector for drone RF signatures.

    Uses pattern matching and machine learning techniques to identify drones.
    """

    def __init__(self, analyzer: RFSignalAnalyzer):
        """
        Initialize drone detector.

        Args:
            analyzer: RF signal analyzer instance
        """
        self.analyzer = analyzer
        self.detected_drones = {}
        self.confidence_threshold = 0.7

        logger.info("Drone Signature Detector initialized")

    def analyze_for_drones(self, samples: np.ndarray, center_freq: float) -> List[Dict[str, Any]]:
        """
        Analyze samples for drone signatures.

        Args:
            samples: Complex IQ samples
            center_freq: Center frequency in Hz

        Returns:
            List of drone detections
        """
        # Perform spectral analysis
        spectrum_analysis = self.analyzer.analyze_spectrum(samples)

        drone_detections = []

        # Check each detected signal
        for signal in spectrum_analysis.get('peak_signals', []):
            # Adjust frequency relative to center
            signal['frequency'] += center_freq

            # Match against known patterns
            pattern = self.analyzer.match_pattern(signal)

            if pattern:
                confidence = self._calculate_confidence(signal, pattern)

                if confidence >= self.confidence_threshold:
                    detection = {
                        'type': 'drone',
                        'model': pattern.name,
                        'frequency': signal['frequency'],
                        'confidence': confidence,
                        'power_dbm': signal['power_dbm'],
                        'bandwidth': signal['bandwidth'],
                    }
                    drone_detections.append(detection)

                    logger.info(f"Drone detected: {pattern.name} @ {signal['frequency']/1e9:.3f} GHz (confidence: {confidence:.2f})")

        return drone_detections

    def _calculate_confidence(self, signal: Dict[str, Any], pattern: SignalPattern) -> float:
        """
        Calculate confidence score for pattern match.

        Args:
            signal: Detected signal info
            pattern: Matched pattern

        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence for frequency match

        # Bandwidth match
        if 'bandwidth' in signal and signal['bandwidth'] > 0:
            bw_ratio = signal['bandwidth'] / pattern.bandwidth
            bw_score = 1.0 - min(abs(1.0 - bw_ratio), 1.0)
            confidence += bw_score * 0.3

        # Power level match
        if 'power_dbm' in signal and 'typical_power' in pattern.characteristics:
            power_diff = abs(signal['power_dbm'] - pattern.characteristics['typical_power'])
            power_score = max(0, 1.0 - power_diff / 20.0)
            confidence += power_score * 0.2

        return min(confidence, 1.0)


import time

if __name__ == "__main__":
    # Test signal analysis
    logging.basicConfig(level=logging.INFO)

    # Create analyzer
    analyzer = RFSignalAnalyzer(sample_rate=2.4e6)

    # Generate test signal (simulated)
    t = np.arange(0, 0.001, 1/2.4e6)
    # Carrier + modulation
    test_signal = np.exp(1j * 2 * np.pi * 100e3 * t)  # 100 kHz offset
    test_signal += 0.1 * np.random.randn(len(t)) + 0.1j * np.random.randn(len(t))  # Add noise

    # Analyze
    analysis = analyzer.analyze_spectrum(test_signal)

    print(f"Detected {analysis['num_signals']} signals")
    print(f"SNR estimate: {analysis['snr_estimate']:.2f} dB")

    # Test drone detection
    drone_detector = DroneSignatureDetector(analyzer)
    drones = drone_detector.analyze_for_drones(test_signal, center_freq=2.4e9)

    print(f"Detected {len(drones)} drones")

"""
Pixelscape Consciousness Renderer - Real-time Avatar Visualization.

Renders Cortana's consciousness state as real-time visual animations.
"""

import threading
import logging
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class ConsciousnessRenderer:
    """
    Renders AI consciousness state as pixel animations.

    Displays:
    - Emotional state (color)
    - Thinking activity (pulse/animation)
    - System health (intensity)
    - Neural activity (patterns)
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize consciousness renderer.

        Args:
            config: Configuration object
        """
        self.config = config or {}
        self.running = False
        self.render_thread: Optional[threading.Thread] = None

        # Display configuration
        self.display_width = self.config.get('display_width', 64)
        self.display_height = self.config.get('display_height', 64)
        self.fps = self.config.get('render_fps', 30)

        # Consciousness visualization state
        self.viz_state = {
            'emotional_color': (0, 200, 255),  # Cortana blue
            'thinking_intensity': 0.0,
            'pulse_rate': 1.0,  # Hz
            'neural_activity': np.zeros((8, 8)),
            'health_score': 1.0
        }

        # Animation state
        self.animation_time = 0.0

        # Thread safety
        self.lock = threading.Lock()

        # Frame buffer
        self.current_frame: Optional[np.ndarray] = None

        logger.info(f"Consciousness Renderer initialized ({self.display_width}x{self.display_height})")

    def start(self):
        """Start rendering loop."""
        if self.running:
            logger.warning("Renderer already running")
            return

        self.running = True
        self.render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self.render_thread.start()

        logger.info("Consciousness Renderer started")

    def _render_loop(self):
        """Main rendering loop."""
        frame_time = 1.0 / self.fps

        while self.running:
            try:
                start_time = time.time()

                # Generate frame
                frame = self._generate_frame()

                # Store frame
                with self.lock:
                    self.current_frame = frame

                # Display frame (if display hardware available)
                self._display_frame(frame)

                # Update animation time
                self.animation_time += frame_time

                # Sleep to maintain target FPS
                elapsed = time.time() - start_time
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

            except Exception as e:
                logger.error(f"Render error: {e}")
                time.sleep(frame_time)

    def _generate_frame(self) -> np.ndarray:
        """
        Generate visualization frame.

        Returns:
            RGB frame as numpy array
        """
        with self.lock:
            # Create base canvas
            frame = np.zeros((self.display_height, self.display_width, 3), dtype=np.uint8)

            # Render consciousness pulse
            pulse = self._generate_pulse()
            frame = self._apply_pulse(frame, pulse)

            # Render neural activity overlay
            frame = self._render_neural_activity(frame)

            # Apply health modulation
            frame = self._apply_health_modulation(frame)

            return frame

    def _generate_pulse(self) -> float:
        """
        Generate pulsing animation based on consciousness state.

        Returns:
            Pulse value (0.0 to 1.0)
        """
        with self.lock:
            pulse_rate = self.viz_state['pulse_rate']
            thinking_intensity = self.viz_state['thinking_intensity']

        # Sine wave pulse
        base_pulse = 0.5 + 0.5 * np.sin(2 * np.pi * pulse_rate * self.animation_time)

        # Modulate by thinking intensity
        pulse = base_pulse * (0.3 + 0.7 * thinking_intensity)

        return pulse

    def _apply_pulse(self, frame: np.ndarray, pulse: float) -> np.ndarray:
        """
        Apply pulsing effect to frame.

        Args:
            frame: Input frame
            pulse: Pulse value (0.0 to 1.0)

        Returns:
            Modified frame
        """
        with self.lock:
            color = np.array(self.viz_state['emotional_color'])

        # Apply pulse to color
        pulsed_color = (color * pulse).astype(np.uint8)

        # Create radial gradient
        center_x, center_y = self.display_width // 2, self.display_height // 2
        y, x = np.ogrid[:self.display_height, :self.display_width]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)

        # Normalize distance to 0-1
        normalized_distance = distance / max_distance

        # Apply radial gradient
        for c in range(3):
            frame[:, :, c] = (pulsed_color[c] * (1 - normalized_distance)).astype(np.uint8)

        return frame

    def _render_neural_activity(self, frame: np.ndarray) -> np.ndarray:
        """
        Overlay neural activity visualization.

        Args:
            frame: Input frame

        Returns:
            Modified frame with neural overlay
        """
        with self.lock:
            activity = self.viz_state['neural_activity']

        # Scale activity to frame size
        cell_height = self.display_height // activity.shape[0]
        cell_width = self.display_width // activity.shape[1]

        # Render active neurons as brighter spots
        for i in range(activity.shape[0]):
            for j in range(activity.shape[1]):
                if activity[i, j] > 0.5:
                    # Calculate cell position
                    y_start = i * cell_height
                    y_end = (i + 1) * cell_height
                    x_start = j * cell_width
                    x_end = (j + 1) * cell_width

                    # Add white sparkle
                    sparkle_intensity = int(255 * activity[i, j])
                    frame[y_start:y_end, x_start:x_end] = np.clip(
                        frame[y_start:y_end, x_start:x_end] + sparkle_intensity,
                        0,
                        255
                    )

        return frame

    def _apply_health_modulation(self, frame: np.ndarray) -> np.ndarray:
        """
        Modulate visualization based on system health.

        Args:
            frame: Input frame

        Returns:
            Modified frame
        """
        with self.lock:
            health_score = self.viz_state['health_score']

        # Reduce intensity if health is poor
        frame = (frame * health_score).astype(np.uint8)

        return frame

    def _display_frame(self, frame: np.ndarray):
        """
        Output frame to display hardware.

        Args:
            frame: RGB frame to display (H x W x 3 RGB array)
        """
        # Initialize display backend if not done
        if not hasattr(self, 'display_backend'):
            self.display_backend = self._init_display_backend()

        # Output to display backend
        if self.display_backend:
            try:
                self.display_backend.show(frame)
            except Exception as e:
                logger.error(f"Display error: {e}")

    def _init_display_backend(self):
        """
        Initialize display backend based on available hardware.

        Returns:
            Display backend instance or None
        """
        display_type = self.config.get('display_type', 'auto')

        if display_type == 'auto':
            # Auto-detect available display hardware
            backend = (
                self._try_init_led_matrix() or
                self._try_init_oled() or
                self._try_init_window() or
                self._init_file_backend()
            )
        elif display_type == 'led':
            backend = self._try_init_led_matrix()
        elif display_type == 'oled':
            backend = self._try_init_oled()
        elif display_type == 'window':
            backend = self._try_init_window()
        elif display_type == 'file':
            backend = self._init_file_backend()
        else:
            logger.warning(f"Unknown display type: {display_type}")
            backend = None

        if backend:
            logger.info(f"Using display backend: {backend.name}")
        else:
            logger.warning("No display backend available")

        return backend

    def _try_init_led_matrix(self):
        """Try to initialize LED matrix display (WS2812B via GPIO)."""
        try:
            from .display_backends import LEDMatrixBackend
            backend = LEDMatrixBackend(
                width=self.display_width,
                height=self.display_height,
                gpio_pin=self.config.get('led_gpio_pin', 18)
            )
            if backend.initialize():
                return backend
        except ImportError:
            logger.debug("LED matrix backend not available")
        except Exception as e:
            logger.debug(f"Failed to init LED matrix: {e}")
        return None

    def _try_init_oled(self):
        """Try to initialize OLED display (I2C/SPI)."""
        try:
            from .display_backends import OLEDBackend
            backend = OLEDBackend(
                width=self.display_width,
                height=self.display_height
            )
            if backend.initialize():
                return backend
        except ImportError:
            logger.debug("OLED backend not available")
        except Exception as e:
            logger.debug(f"Failed to init OLED: {e}")
        return None

    def _try_init_window(self):
        """Try to initialize window display (OpenCV/Pygame)."""
        try:
            from .display_backends import WindowBackend
            backend = WindowBackend(
                width=self.display_width,
                height=self.display_height
            )
            if backend.initialize():
                return backend
        except ImportError:
            logger.debug("Window backend not available")
        except Exception as e:
            logger.debug(f"Failed to init window: {e}")
        return None

    def _init_file_backend(self):
        """Initialize file output backend (fallback)."""
        try:
            from .display_backends import FileBackend
            backend = FileBackend(
                output_dir=self.config.get('output_dir', '/tmp/sentient-frames')
            )
            backend.initialize()
            return backend
        except Exception as e:
            logger.error(f"Failed to init file backend: {e}")
            return None

    def update_state(self, state_update: Dict[str, Any]):
        """
        Update visualization state.

        Args:
            state_update: Dictionary with state updates
        """
        with self.lock:
            if 'emotional_state' in state_update:
                self.viz_state['emotional_color'] = self._emotion_to_color(
                    state_update['emotional_state']
                )

            if 'thinking_intensity' in state_update:
                self.viz_state['thinking_intensity'] = state_update['thinking_intensity']

            if 'pulse_rate' in state_update:
                self.viz_state['pulse_rate'] = state_update['pulse_rate']

            if 'neural_activity' in state_update:
                self.viz_state['neural_activity'] = state_update['neural_activity']

            if 'health_score' in state_update:
                self.viz_state['health_score'] = state_update['health_score']

    def _emotion_to_color(self, emotion: str) -> Tuple[int, int, int]:
        """
        Map emotional state to RGB color.

        Args:
            emotion: Emotional state string

        Returns:
            RGB color tuple
        """
        emotion_map = {
            'focused': (0, 200, 255),      # Cortana blue
            'thinking': (100, 150, 255),   # Deeper blue
            'alert': (255, 150, 0),        # Orange
            'processing': (150, 0, 255),   # Purple
            'idle': (0, 100, 150),         # Dim blue
            'satisfied': (0, 255, 100),    # Green
            'concerned': (255, 255, 0)     # Yellow
        }

        return emotion_map.get(emotion, (0, 200, 255))

    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        Get current rendered frame.

        Returns:
            RGB frame or None
        """
        with self.lock:
            return self.current_frame.copy() if self.current_frame is not None else None

    def save_frame(self, filepath: str):
        """
        Save current frame to file.

        Args:
            filepath: Path to save image
        """
        frame = self.get_current_frame()
        if frame is None:
            logger.warning("No frame to save")
            return

        try:
            # Try using PIL if available
            from PIL import Image
            img = Image.fromarray(frame, 'RGB')
            img.save(filepath)
            logger.info(f"Frame saved to {filepath}")

        except ImportError:
            # Fallback to OpenCV
            import cv2
            cv2.imwrite(filepath, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            logger.info(f"Frame saved to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save frame: {e}")

    def stop(self):
        """Stop renderer."""
        self.running = False

        if self.render_thread:
            self.render_thread.join(timeout=2)

        logger.info("Consciousness Renderer stopped")

    def __repr__(self) -> str:
        return f"<ConsciousnessRenderer(size={self.display_width}x{self.display_height}, fps={self.fps}, running={self.running})>"

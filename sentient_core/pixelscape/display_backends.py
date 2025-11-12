"""
Display backends for consciousness renderer.

Supports multiple display types:
- LED Matrix (WS2812B via GPIO)
- OLED Display (I2C/SPI)
- Window Display (OpenCV/Pygame)
- File Output (PNG frames)
"""

import logging
import numpy as np
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class DisplayBackend(ABC):
    """Abstract base class for display backends."""

    def __init__(self, width: int, height: int):
        """
        Initialize display backend.

        Args:
            width: Display width in pixels
            height: Display height in pixels
        """
        self.width = width
        self.height = height
        self.name = "Unknown"

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize display hardware.

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def show(self, frame: np.ndarray):
        """
        Display a frame.

        Args:
            frame: RGB frame array (H x W x 3)
        """
        pass

    @abstractmethod
    def shutdown(self):
        """Cleanup display resources."""
        pass


class LEDMatrixBackend(DisplayBackend):
    """
    LED Matrix display backend using WS2812B LEDs.

    Requires: rpi_ws281x library
    Hardware: Raspberry Pi with GPIO
    """

    def __init__(self, width: int, height: int, gpio_pin: int = 18, brightness: int = 128):
        """
        Initialize LED matrix backend.

        Args:
            width: Matrix width
            height: Matrix height
            gpio_pin: GPIO pin number (BCM)
            brightness: LED brightness (0-255)
        """
        super().__init__(width, height)
        self.name = "LED Matrix"
        self.gpio_pin = gpio_pin
        self.brightness = brightness
        self.strip = None

    def initialize(self) -> bool:
        """Initialize LED strip."""
        try:
            from rpi_ws281x import PixelStrip, Color

            # LED strip configuration
            LED_COUNT = self.width * self.height
            LED_PIN = self.gpio_pin
            LED_FREQ_HZ = 800000
            LED_DMA = 10
            LED_BRIGHTNESS = self.brightness
            LED_INVERT = False
            LED_CHANNEL = 0

            self.strip = PixelStrip(
                LED_COUNT,
                LED_PIN,
                LED_FREQ_HZ,
                LED_DMA,
                LED_INVERT,
                LED_BRIGHTNESS,
                LED_CHANNEL
            )

            self.strip.begin()
            logger.info(f"LED matrix initialized: {self.width}x{self.height} on GPIO {self.gpio_pin}")
            return True

        except ImportError:
            logger.warning("rpi_ws281x not available - install with: pip install rpi_ws281x")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize LED matrix: {e}")
            return False

    def show(self, frame: np.ndarray):
        """Display frame on LED matrix."""
        if not self.strip:
            return

        try:
            from rpi_ws281x import Color

            # Resize frame if needed
            if frame.shape[:2] != (self.height, self.width):
                from PIL import Image
                pil_frame = Image.fromarray(frame)
                pil_frame = pil_frame.resize((self.width, self.height))
                frame = np.array(pil_frame)

            # Convert to LED colors
            for y in range(self.height):
                for x in range(self.width):
                    r, g, b = frame[y, x]

                    # Calculate LED index (may need adjustment based on wiring)
                    # Assuming zigzag pattern
                    if y % 2 == 0:
                        index = y * self.width + x
                    else:
                        index = y * self.width + (self.width - 1 - x)

                    # Set LED color
                    self.strip.setPixelColor(index, Color(int(r), int(g), int(b)))

            # Update strip
            self.strip.show()

        except Exception as e:
            logger.error(f"LED matrix display error: {e}")

    def shutdown(self):
        """Shutdown LED matrix."""
        if self.strip:
            # Clear all LEDs
            for i in range(self.width * self.height):
                self.strip.setPixelColor(i, 0)
            self.strip.show()
        logger.info("LED matrix shutdown")


class OLEDBackend(DisplayBackend):
    """
    OLED display backend for small displays (SSD1306, etc.).

    Requires: Adafruit CircuitPython libraries
    Hardware: I2C/SPI OLED display
    """

    def __init__(self, width: int, height: int):
        """Initialize OLED backend."""
        super().__init__(width, height)
        self.name = "OLED"
        self.display = None

    def initialize(self) -> bool:
        """Initialize OLED display."""
        try:
            import board
            import busio
            from adafruit_ssd1306 import SSD1306_I2C

            # Create I2C interface
            i2c = busio.I2C(board.SCL, board.SDA)

            # Create display
            self.display = SSD1306_I2C(self.width, self.height, i2c)

            # Clear display
            self.display.fill(0)
            self.display.show()

            logger.info(f"OLED display initialized: {self.width}x{self.height}")
            return True

        except ImportError:
            logger.warning("Adafruit CircuitPython libraries not available")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize OLED: {e}")
            return False

    def show(self, frame: np.ndarray):
        """Display frame on OLED."""
        if not self.display:
            return

        try:
            from PIL import Image

            # Convert to grayscale
            if len(frame.shape) == 3:
                gray = np.mean(frame, axis=2).astype(np.uint8)
            else:
                gray = frame

            # Resize if needed
            if gray.shape != (self.height, self.width):
                pil_image = Image.fromarray(gray)
                pil_image = pil_image.resize((self.width, self.height))
                gray = np.array(pil_image)

            # Convert to binary (threshold at 128)
            binary = (gray > 128).astype(np.uint8) * 255

            # Create PIL image
            image = Image.fromarray(binary, mode='L')

            # Display
            self.display.image(image)
            self.display.show()

        except Exception as e:
            logger.error(f"OLED display error: {e}")

    def shutdown(self):
        """Shutdown OLED display."""
        if self.display:
            self.display.fill(0)
            self.display.show()
        logger.info("OLED display shutdown")


class WindowBackend(DisplayBackend):
    """
    Window display backend using OpenCV or Pygame.

    Useful for development and testing.
    """

    def __init__(self, width: int, height: int, scale: int = 4):
        """
        Initialize window backend.

        Args:
            width: Display width
            height: Display height
            scale: Scale factor for window size
        """
        super().__init__(width, height)
        self.name = "Window"
        self.scale = scale
        self.window_name = "Sentient Consciousness"
        self.use_opencv = False

    def initialize(self) -> bool:
        """Initialize window display."""
        try:
            import cv2
            self.use_opencv = True
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, self.width * self.scale, self.height * self.scale)
            logger.info(f"OpenCV window initialized: {self.width}x{self.height}")
            return True

        except ImportError:
            logger.warning("OpenCV not available, trying pygame...")

            try:
                import pygame
                pygame.init()
                self.screen = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
                pygame.display.set_caption(self.window_name)
                self.use_opencv = False
                logger.info(f"Pygame window initialized: {self.width}x{self.height}")
                return True

            except ImportError:
                logger.warning("Neither OpenCV nor Pygame available")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize window: {e}")
            return False

    def show(self, frame: np.ndarray):
        """Display frame in window."""
        try:
            if self.use_opencv:
                import cv2

                # Resize frame
                display_frame = cv2.resize(
                    frame,
                    (self.width * self.scale, self.height * self.scale),
                    interpolation=cv2.INTER_NEAREST
                )

                # Convert RGB to BGR for OpenCV
                display_frame = cv2.cvtColor(display_frame, cv2.COLOR_RGB2BGR)

                # Show frame
                cv2.imshow(self.window_name, display_frame)
                cv2.waitKey(1)

            else:
                import pygame

                # Resize frame
                from PIL import Image
                pil_frame = Image.fromarray(frame)
                pil_frame = pil_frame.resize(
                    (self.width * self.scale, self.height * self.scale),
                    Image.NEAREST
                )

                # Convert to pygame surface
                frame_str = pil_frame.tobytes()
                surface = pygame.image.fromstring(
                    frame_str,
                    (self.width * self.scale, self.height * self.scale),
                    'RGB'
                )

                # Blit and update
                self.screen.blit(surface, (0, 0))
                pygame.display.flip()

                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

        except Exception as e:
            logger.error(f"Window display error: {e}")

    def shutdown(self):
        """Shutdown window display."""
        try:
            if self.use_opencv:
                import cv2
                cv2.destroyAllWindows()
            else:
                import pygame
                pygame.quit()
        except Exception:
            pass  # Ignore errors during shutdown
        logger.info("Window display shutdown")


class FileBackend(DisplayBackend):
    """
    File output backend for saving frames to disk.

    Useful for debugging and creating video recordings.
    """

    def __init__(self, width: int = 64, height: int = 64, output_dir: str = "/tmp/sentient-frames"):
        """
        Initialize file backend.

        Args:
            width: Frame width
            height: Frame height
            output_dir: Directory to save frames
        """
        super().__init__(width, height)
        self.name = "File"
        self.output_dir = Path(output_dir)
        self.frame_count = 0

    def initialize(self) -> bool:
        """Initialize file output."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"File output initialized: {self.output_dir}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize file output: {e}")
            return False

    def show(self, frame: np.ndarray):
        """Save frame to file."""
        try:
            from PIL import Image

            # Create filename
            filename = self.output_dir / f"frame_{self.frame_count:06d}.png"

            # Convert to PIL and save
            image = Image.fromarray(frame.astype('uint8'))
            image.save(filename)

            self.frame_count += 1

            # Log every 100 frames
            if self.frame_count % 100 == 0:
                logger.info(f"Saved {self.frame_count} frames to {self.output_dir}")

        except Exception as e:
            logger.error(f"File output error: {e}")

    def shutdown(self):
        """Cleanup file output."""
        logger.info(f"File output complete: {self.frame_count} frames saved to {self.output_dir}")


# Factory function
def create_display_backend(backend_type: str, width: int = 64, height: int = 64, **kwargs) -> Optional[DisplayBackend]:
    """
    Create a display backend.

    Args:
        backend_type: Type of backend ('led', 'oled', 'window', 'file')
        width: Display width
        height: Display height
        **kwargs: Additional backend-specific arguments

    Returns:
        Display backend instance or None
    """
    backends = {
        'led': LEDMatrixBackend,
        'oled': OLEDBackend,
        'window': WindowBackend,
        'file': FileBackend,
    }

    if backend_type not in backends:
        logger.error(f"Unknown backend type: {backend_type}")
        return None

    try:
        backend_class = backends[backend_type]
        backend = backend_class(width, height, **kwargs)

        if backend.initialize():
            return backend
        else:
            return None

    except Exception as e:
        logger.error(f"Failed to create {backend_type} backend: {e}")
        return None

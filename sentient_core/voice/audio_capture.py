"""
Real-time audio capture and streaming for voice input.
"""

import logging
import asyncio
import threading
from typing import Optional, Callable, Any
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)


class AudioCapture:
    """
    Real-time audio capture system for microphone input.

    Features:
    - Real-time audio streaming from microphone
    - Voice activity detection (VAD)
    - Buffering and chunking
    - Callback support for processing
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        buffer_duration: float = 2.0
    ):
        """
        Initialize audio capture.

        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1=mono, 2=stereo)
            chunk_size: Size of audio chunks to capture
            buffer_duration: Buffer duration in seconds
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.buffer_duration = buffer_duration
        self.buffer_size = int(sample_rate * buffer_duration)

        # Audio stream
        self.stream = None
        self.audio_interface = None

        # Buffer
        self.buffer = deque(maxlen=self.buffer_size)

        # State
        self.is_capturing = False
        self.capture_thread = None

        # Callbacks
        self.audio_callback: Optional[Callable] = None
        self.vad_callback: Optional[Callable] = None

        # Voice activity detection
        self.vad_threshold = 0.02  # RMS threshold for VAD
        self.is_speech_active = False

        logger.info(f"AudioCapture initialized: {sample_rate}Hz, {channels}ch")

    def initialize(self) -> bool:
        """
        Initialize audio input device.

        Returns:
            True if successful
        """
        try:
            import pyaudio

            self.audio_interface = pyaudio.PyAudio()

            # Get default input device info
            device_info = self.audio_interface.get_default_input_device_info()
            logger.info(f"Using audio device: {device_info['name']}")

            # Open audio stream
            self.stream = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._stream_callback
            )

            logger.info("Audio capture initialized successfully")
            return True

        except ImportError:
            logger.error("pyaudio not available - install with: pip install pyaudio")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize audio capture: {e}")
            return False

    def _stream_callback(self, in_data, frame_count, time_info, status):
        """PyAudio stream callback."""
        import pyaudio

        if status:
            logger.warning(f"Audio stream status: {status}")

        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)

        # Add to buffer
        self.buffer.extend(audio_data)

        # Voice activity detection
        rms = self._calculate_rms(audio_data)
        speech_active = rms > self.vad_threshold

        if speech_active != self.is_speech_active:
            self.is_speech_active = speech_active
            if self.vad_callback:
                self.vad_callback(speech_active)

        # Call audio callback if registered
        if self.audio_callback:
            self.audio_callback(audio_data)

        return (in_data, pyaudio.paContinue)

    def _calculate_rms(self, audio_data: np.ndarray) -> float:
        """
        Calculate RMS (Root Mean Square) energy of audio.

        Args:
            audio_data: Audio data array

        Returns:
            RMS value
        """
        # Normalize to -1.0 to 1.0
        normalized = audio_data.astype(np.float32) / 32768.0
        rms = np.sqrt(np.mean(normalized ** 2))
        return float(rms)

    def start(self):
        """Start audio capture."""
        if not self.stream:
            logger.error("Audio stream not initialized")
            return

        if self.is_capturing:
            logger.warning("Already capturing audio")
            return

        logger.info("Starting audio capture...")
        self.stream.start_stream()
        self.is_capturing = True

    def stop(self):
        """Stop audio capture."""
        if not self.is_capturing:
            return

        logger.info("Stopping audio capture...")

        if self.stream:
            self.stream.stop_stream()

        self.is_capturing = False

    def get_buffer(self) -> np.ndarray:
        """
        Get current audio buffer.

        Returns:
            Audio buffer as numpy array
        """
        return np.array(list(self.buffer), dtype=np.int16)

    def clear_buffer(self):
        """Clear audio buffer."""
        self.buffer.clear()

    def capture_chunk(self, duration: float = 1.0) -> Optional[np.ndarray]:
        """
        Capture a single chunk of audio.

        Args:
            duration: Duration in seconds to capture

        Returns:
            Audio data array
        """
        if not self.stream:
            logger.error("Audio stream not initialized")
            return None

        try:
            num_frames = int(self.sample_rate * duration)
            chunks = []

            # Capture frames
            for _ in range(0, num_frames, self.chunk_size):
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                chunk = np.frombuffer(data, dtype=np.int16)
                chunks.append(chunk)

            # Concatenate chunks
            audio_data = np.concatenate(chunks)

            return audio_data

        except Exception as e:
            logger.error(f"Failed to capture audio chunk: {e}")
            return None

    def capture_until_silence(
        self,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.0,
        max_duration: float = 30.0
    ) -> Optional[np.ndarray]:
        """
        Capture audio until silence is detected.

        Args:
            silence_threshold: RMS threshold for silence
            silence_duration: Duration of silence to stop (seconds)
            max_duration: Maximum capture duration (seconds)

        Returns:
            Captured audio data
        """
        logger.info("Capturing audio until silence...")

        chunks = []
        silence_chunks = 0
        max_chunks = int(max_duration * self.sample_rate / self.chunk_size)
        silence_chunks_needed = int(silence_duration * self.sample_rate / self.chunk_size)

        try:
            for i in range(max_chunks):
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                chunk = np.frombuffer(data, dtype=np.int16)
                chunks.append(chunk)

                # Check for silence
                rms = self._calculate_rms(chunk)

                if rms < silence_threshold:
                    silence_chunks += 1
                    if silence_chunks >= silence_chunks_needed:
                        logger.info(f"Silence detected after {i * self.chunk_size / self.sample_rate:.2f}s")
                        break
                else:
                    silence_chunks = 0

            # Concatenate chunks
            audio_data = np.concatenate(chunks)

            logger.info(f"Captured {len(audio_data) / self.sample_rate:.2f}s of audio")
            return audio_data

        except Exception as e:
            logger.error(f"Failed to capture audio: {e}")
            return None

    def register_audio_callback(self, callback: Callable[[np.ndarray], None]):
        """
        Register callback for audio data.

        Args:
            callback: Function to call with audio chunks
        """
        self.audio_callback = callback

    def register_vad_callback(self, callback: Callable[[bool], None]):
        """
        Register callback for voice activity detection.

        Args:
            callback: Function to call when speech starts/stops
        """
        self.vad_callback = callback

    def set_vad_threshold(self, threshold: float):
        """
        Set voice activity detection threshold.

        Args:
            threshold: RMS threshold (0.0-1.0)
        """
        self.vad_threshold = threshold
        logger.info(f"VAD threshold set to: {threshold}")

    async def capture_async(self, duration: float = 1.0) -> Optional[np.ndarray]:
        """
        Asynchronously capture audio.

        Args:
            duration: Duration to capture in seconds

        Returns:
            Audio data array
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.capture_chunk, duration)

    def get_info(self) -> dict:
        """Get audio capture information."""
        return {
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'chunk_size': self.chunk_size,
            'buffer_size': self.buffer_size,
            'is_capturing': self.is_capturing,
            'is_speech_active': self.is_speech_active,
            'buffer_filled': len(self.buffer),
        }

    def list_devices(self) -> list:
        """
        List available audio input devices.

        Returns:
            List of device information
        """
        if not self.audio_interface:
            try:
                import pyaudio
                self.audio_interface = pyaudio.PyAudio()
            except ImportError:
                logger.error("pyaudio not available")
                return []

        devices = []
        for i in range(self.audio_interface.get_device_count()):
            device_info = self.audio_interface.get_device_info_by_index(i)

            # Only include input devices
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                })

        return devices

    def shutdown(self):
        """Shutdown audio capture."""
        logger.info("Shutting down audio capture...")

        self.stop()

        if self.stream:
            self.stream.close()
            self.stream = None

        if self.audio_interface:
            self.audio_interface.terminate()
            self.audio_interface = None

        logger.info("Audio capture shutdown complete")


class StreamingTranscriber:
    """
    Real-time streaming speech transcription.

    Combines audio capture with continuous transcription.
    """

    def __init__(self, voice_processor, sample_rate: int = 16000):
        """
        Initialize streaming transcriber.

        Args:
            voice_processor: VoiceProcessor instance for transcription
            sample_rate: Audio sample rate
        """
        self.voice_processor = voice_processor
        self.sample_rate = sample_rate

        # Audio capture
        self.audio_capture = AudioCapture(sample_rate=sample_rate)

        # Transcription buffer
        self.transcription_buffer = []

        # State
        self.is_streaming = False

        logger.info("StreamingTranscriber initialized")

    def initialize(self) -> bool:
        """Initialize streaming transcriber."""
        return self.audio_capture.initialize()

    def start_streaming(self, callback: Optional[Callable[[str], None]] = None):
        """
        Start streaming transcription.

        Args:
            callback: Optional callback for transcription results
        """
        logger.info("Starting streaming transcription...")

        # Register audio callback
        def audio_callback(audio_chunk):
            # Transcribe chunk
            if len(audio_chunk) > self.sample_rate * 0.5:  # Min 0.5s
                text = self.voice_processor.transcribe(audio_chunk)
                self.transcription_buffer.append(text)

                if callback:
                    callback(text)

        self.audio_capture.register_audio_callback(audio_callback)

        # Start capture
        self.audio_capture.start()
        self.is_streaming = True

    def stop_streaming(self) -> str:
        """
        Stop streaming and return full transcription.

        Returns:
            Combined transcription text
        """
        logger.info("Stopping streaming transcription...")

        self.audio_capture.stop()
        self.is_streaming = False

        # Combine transcriptions
        full_text = " ".join(self.transcription_buffer)
        self.transcription_buffer.clear()

        return full_text

    def get_transcription(self) -> str:
        """Get current transcription buffer."""
        return " ".join(self.transcription_buffer)

    def shutdown(self):
        """Shutdown streaming transcriber."""
        self.audio_capture.shutdown()


if __name__ == "__main__":
    # Test audio capture
    logging.basicConfig(level=logging.INFO)

    capture = AudioCapture()

    if capture.initialize():
        print("Available audio devices:")
        for device in capture.list_devices():
            print(f"  [{device['index']}] {device['name']}")

        print("\nCapturing 3 seconds of audio...")
        capture.start()

        import time
        time.sleep(3)

        capture.stop()

        buffer = capture.get_buffer()
        print(f"Captured {len(buffer)} samples ({len(buffer) / capture.sample_rate:.2f}s)")

        capture.shutdown()
    else:
        print("Failed to initialize audio capture")

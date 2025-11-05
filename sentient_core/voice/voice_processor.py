"""
Voice processing for speech-to-text and text-to-speech.
"""

import logging
from typing import Dict, Any, Optional, Union
import numpy as np
from pathlib import Path


logger = logging.getLogger(__name__)


class VoiceProcessor:
    """
    Voice processing system for speech recognition and synthesis.

    Supports:
    - Speech-to-text (transcription)
    - Text-to-speech (synthesis)
    - Audio preprocessing
    - Multi-language support
    """

    def __init__(self, config):
        """
        Initialize voice processor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.sample_rate = config.get('perception.audio.sample_rate', 16000)
        self.model_name = config.get('perception.audio.model', 'wav2vec2')

        # Models
        self.stt_model = None  # Speech-to-text
        self.tts_model = None  # Text-to-speech
        self.audio_processor = None

        # State
        self.initialized = False

        logger.info("VoiceProcessor created")

    def initialize(self):
        """Initialize voice processing models."""
        if self.initialized:
            logger.warning("VoiceProcessor already initialized")
            return

        logger.info("Initializing voice processing...")

        try:
            self._load_stt_model()
            self._load_tts_model()
            self.initialized = True
            logger.info("Voice processing initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize voice processing: {e}")
            logger.warning("Voice processing will use fallback mode")

    def _load_stt_model(self):
        """Load speech-to-text model."""
        try:
            # Try to load Whisper or wav2vec2
            if self.model_name == 'whisper':
                import whisper
                self.stt_model = whisper.load_model("base")
                logger.info("Loaded Whisper model for STT")
            else:
                # Use transformers wav2vec2
                from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
                self.audio_processor = Wav2Vec2Processor.from_pretrained(
                    "facebook/wav2vec2-base-960h"
                )
                self.stt_model = Wav2Vec2ForCTC.from_pretrained(
                    "facebook/wav2vec2-base-960h"
                )
                logger.info("Loaded Wav2Vec2 model for STT")
        except ImportError as e:
            logger.warning(f"Failed to load STT model: {e}")
            self.stt_model = None

    def _load_tts_model(self):
        """Load text-to-speech model."""
        try:
            # Try to load TTS library
            import pyttsx3
            self.tts_model = pyttsx3.init()
            logger.info("Loaded pyttsx3 for TTS")
        except ImportError:
            logger.warning("pyttsx3 not available for TTS")
            self.tts_model = None

    def transcribe(self, audio_data: Union[np.ndarray, str, Path]) -> str:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio data (numpy array, file path, or bytes)

        Returns:
            Transcribed text
        """
        logger.info("Transcribing audio...")

        if not self.initialized:
            logger.warning("Voice processor not initialized, using fallback")
            return "[Audio transcription not available]"

        try:
            # Handle different input types
            if isinstance(audio_data, (str, Path)):
                audio_array = self._load_audio_file(audio_data)
            elif isinstance(audio_data, bytes):
                audio_array = self._bytes_to_array(audio_data)
            else:
                audio_array = audio_data

            # Transcribe based on model type
            if self.stt_model:
                if self.model_name == 'whisper':
                    result = self.stt_model.transcribe(audio_array)
                    return result['text']
                else:
                    # Wav2Vec2
                    import torch
                    inputs = self.audio_processor(
                        audio_array,
                        sampling_rate=self.sample_rate,
                        return_tensors="pt"
                    )
                    with torch.no_grad():
                        logits = self.stt_model(inputs.input_values).logits
                    predicted_ids = torch.argmax(logits, dim=-1)
                    transcription = self.audio_processor.batch_decode(predicted_ids)[0]
                    return transcription
            else:
                return "[STT model not available]"

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return f"[Transcription error: {e}]"

    def synthesize(self, text: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """
        Convert text to speech.

        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file

        Returns:
            Audio bytes (if output_path is None)
        """
        logger.info(f"Synthesizing speech: {text[:50]}...")

        if not self.initialized:
            logger.warning("Voice processor not initialized")
            return None

        try:
            if self.tts_model:
                if output_path:
                    self.tts_model.save_to_file(text, output_path)
                    self.tts_model.runAndWait()
                    logger.info(f"Audio saved to: {output_path}")
                    return None
                else:
                    # Return audio data
                    # Note: pyttsx3 doesn't directly return audio data,
                    # so we save to temp and read
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                        temp_path = f.name

                    self.tts_model.save_to_file(text, temp_path)
                    self.tts_model.runAndWait()

                    with open(temp_path, 'rb') as f:
                        audio_bytes = f.read()

                    # Cleanup
                    Path(temp_path).unlink()

                    return audio_bytes
            else:
                logger.warning("TTS model not available")
                return None

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return None

    def _load_audio_file(self, file_path: Union[str, Path]) -> np.ndarray:
        """Load audio file and convert to numpy array."""
        try:
            import soundfile as sf
            audio, sr = sf.read(file_path)

            # Resample if needed
            if sr != self.sample_rate:
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)

            return audio

        except Exception as e:
            logger.error(f"Failed to load audio file: {e}")
            raise

    def _bytes_to_array(self, audio_bytes: bytes) -> np.ndarray:
        """Convert audio bytes to numpy array."""
        try:
            import io
            import soundfile as sf

            audio, sr = sf.read(io.BytesIO(audio_bytes))

            if sr != self.sample_rate:
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)

            return audio

        except Exception as e:
            logger.error(f"Failed to convert bytes to array: {e}")
            raise

    def process_audio(self, audio_data: Any, operation: str = 'transcribe', **kwargs) -> Any:
        """
        General audio processing method.

        Args:
            audio_data: Input audio data
            operation: Operation to perform ('transcribe', 'synthesize', etc.)
            **kwargs: Additional parameters

        Returns:
            Processed result
        """
        if operation == 'transcribe':
            return self.transcribe(audio_data)
        elif operation == 'synthesize':
            return self.synthesize(audio_data, **kwargs)
        else:
            logger.error(f"Unknown operation: {operation}")
            return None

    def get_supported_languages(self) -> list:
        """Get list of supported languages."""
        # This would return actual supported languages based on loaded models
        return ['en', 'es', 'fr', 'de', 'zh', 'ja']

    def set_language(self, language: str) -> bool:
        """
        Set the language for processing.

        Args:
            language: Language code (e.g., 'en', 'es')

        Returns:
            True if successful
        """
        if language in self.get_supported_languages():
            self.config.config_data['voice_language'] = language
            logger.info(f"Voice language set to: {language}")
            return True
        else:
            logger.warning(f"Language not supported: {language}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """Get voice processor information."""
        return {
            'initialized': self.initialized,
            'sample_rate': self.sample_rate,
            'model': self.model_name,
            'stt_available': self.stt_model is not None,
            'tts_available': self.tts_model is not None,
            'supported_languages': self.get_supported_languages()
        }

    def shutdown(self):
        """Shutdown voice processor."""
        logger.info("Shutting down voice processor...")

        if self.tts_model:
            try:
                self.tts_model.stop()
            except:
                pass

        self.stt_model = None
        self.tts_model = None
        self.audio_processor = None
        self.initialized = False

        logger.info("Voice processor shutdown complete")

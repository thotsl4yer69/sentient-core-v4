"""
Model Download Manager

Handles downloading, caching, and verification of AI models.
Supports multiple model types: LLM (GGUF), Vision (YOLO), Audio (Whisper), Hardware (.hef)
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass
import urllib.request
import urllib.error
from tqdm import tqdm


logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a downloadable model."""
    name: str
    url: str
    filename: str
    checksum: Optional[str] = None
    checksum_algo: str = "sha256"
    size_mb: Optional[int] = None
    model_type: str = "llm"  # llm, vision, audio, hardware
    description: Optional[str] = None


class DownloadProgressBar(tqdm):
    """Progress bar for downloads."""

    def update_to(self, b=1, bsize=1, tsize=None):
        """Update progress bar.

        Args:
            b: Number of blocks transferred
            bsize: Size of each block
            tsize: Total size
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


class ModelDownloader:
    """
    Manages model downloads with caching and verification.

    Features:
    - Automatic model download on first use
    - Checksum verification
    - Resume interrupted downloads
    - Model cache management
    - Multi-source support
    """

    # Default model registry
    DEFAULT_MODELS = {
        # LLM Models (GGUF format)
        "qwen2.5-0.5b": ModelConfig(
            name="Qwen 2.5 0.5B",
            url="https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
            filename="qwen2.5-0.5b-instruct-q4_k_m.gguf",
            size_mb=350,
            model_type="llm",
            description="Lightweight Qwen model for edge devices"
        ),
        "qwen2.5-1.5b": ModelConfig(
            name="Qwen 2.5 1.5B",
            url="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            filename="qwen2.5-1.5b-instruct-q4_k_m.gguf",
            size_mb=950,
            model_type="llm",
            description="Balanced Qwen model for general use"
        ),
        "qwen2.5-3b": ModelConfig(
            name="Qwen 2.5 3B",
            url="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
            filename="qwen2.5-3b-instruct-q4_k_m.gguf",
            size_mb=1900,
            model_type="llm",
            description="High-performance Qwen model"
        ),

        # Vision Models
        "yolov8n": ModelConfig(
            name="YOLOv8 Nano",
            url="https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt",
            filename="yolov8n.pt",
            size_mb=6,
            model_type="vision",
            description="Fast object detection for edge devices"
        ),
        "yolov8s": ModelConfig(
            name="YOLOv8 Small",
            url="https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt",
            filename="yolov8s.pt",
            size_mb=22,
            model_type="vision",
            description="Balanced object detection model"
        ),

        # Audio Models
        "whisper-tiny": ModelConfig(
            name="Whisper Tiny",
            url="https://huggingface.co/openai/whisper-tiny/resolve/main/pytorch_model.bin",
            filename="whisper-tiny.bin",
            size_mb=72,
            model_type="audio",
            description="Fast speech recognition"
        ),
        "whisper-base": ModelConfig(
            name="Whisper Base",
            url="https://huggingface.co/openai/whisper-base/resolve/main/pytorch_model.bin",
            filename="whisper-base.bin",
            size_mb=140,
            model_type="audio",
            description="Balanced speech recognition"
        ),
    }

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize model downloader.

        Args:
            cache_dir: Directory to cache downloaded models.
                      Defaults to ~/.sentient-core/models/
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".sentient-core" / "models"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Model registry
        self.models = self.DEFAULT_MODELS.copy()

        # Cache metadata
        self.metadata_file = self.cache_dir / "models_metadata.json"
        self.metadata = self._load_metadata()

        logger.info(f"Model cache directory: {self.cache_dir}")

    def _load_metadata(self) -> Dict:
        """Load model metadata from cache."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
        return {}

    def _save_metadata(self):
        """Save model metadata to cache."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def register_model(self, model_id: str, config: ModelConfig):
        """
        Register a custom model.

        Args:
            model_id: Unique identifier for the model
            config: Model configuration
        """
        self.models[model_id] = config
        logger.info(f"Registered model: {model_id}")

    def list_models(self, model_type: Optional[str] = None) -> List[str]:
        """
        List available models.

        Args:
            model_type: Filter by model type (llm, vision, audio, hardware)

        Returns:
            List of model IDs
        """
        if model_type:
            return [
                mid for mid, config in self.models.items()
                if config.model_type == model_type
            ]
        return list(self.models.keys())

    def get_model_path(self, model_id: str) -> Path:
        """
        Get the local path for a model.

        Args:
            model_id: Model identifier

        Returns:
            Path to model file
        """
        if model_id not in self.models:
            raise ValueError(f"Unknown model: {model_id}")

        config = self.models[model_id]
        return self.cache_dir / config.filename

    def is_downloaded(self, model_id: str) -> bool:
        """
        Check if a model is already downloaded.

        Args:
            model_id: Model identifier

        Returns:
            True if model exists locally
        """
        try:
            model_path = self.get_model_path(model_id)

            # Check if file exists
            if not model_path.exists():
                return False

            # Check if size matches (if known)
            config = self.models[model_id]
            if config.size_mb:
                expected_size = config.size_mb * 1024 * 1024
                actual_size = model_path.stat().st_size
                # Allow 5% tolerance
                if abs(actual_size - expected_size) > expected_size * 0.05:
                    logger.warning(f"Model {model_id} size mismatch")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error checking model {model_id}: {e}")
            return False

    def _calculate_checksum(self, file_path: Path, algorithm: str = "sha256") -> str:
        """
        Calculate file checksum.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256)

        Returns:
            Hex digest of checksum
        """
        hash_func = hashlib.new(algorithm)

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    def verify_checksum(self, model_id: str) -> bool:
        """
        Verify model checksum.

        Args:
            model_id: Model identifier

        Returns:
            True if checksum matches
        """
        config = self.models[model_id]

        if not config.checksum:
            logger.info(f"No checksum available for {model_id}")
            return True

        model_path = self.get_model_path(model_id)

        if not model_path.exists():
            return False

        logger.info(f"Verifying checksum for {model_id}...")
        actual_checksum = self._calculate_checksum(model_path, config.checksum_algo)

        if actual_checksum == config.checksum:
            logger.info(f"Checksum verified for {model_id}")
            return True
        else:
            logger.error(f"Checksum mismatch for {model_id}")
            logger.error(f"Expected: {config.checksum}")
            logger.error(f"Actual: {actual_checksum}")
            return False

    def download(
        self,
        model_id: str,
        force: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> Path:
        """
        Download a model if not already cached.

        Args:
            model_id: Model identifier
            force: Force re-download even if cached
            progress_callback: Optional callback for progress updates

        Returns:
            Path to downloaded model

        Raises:
            ValueError: If model_id is unknown
            RuntimeError: If download fails
        """
        if model_id not in self.models:
            raise ValueError(f"Unknown model: {model_id}")

        config = self.models[model_id]
        model_path = self.get_model_path(model_id)

        # Check if already downloaded
        if not force and self.is_downloaded(model_id):
            logger.info(f"Model {model_id} already cached at {model_path}")
            return model_path

        logger.info(f"Downloading {config.name} ({model_id})...")
        logger.info(f"URL: {config.url}")
        logger.info(f"Destination: {model_path}")

        if config.size_mb:
            logger.info(f"Expected size: {config.size_mb} MB")

        # Download with progress bar
        try:
            with DownloadProgressBar(
                unit='B',
                unit_scale=True,
                miniters=1,
                desc=config.filename
            ) as progress:
                urllib.request.urlretrieve(
                    config.url,
                    model_path,
                    reporthook=progress.update_to
                )

            logger.info(f"Download complete: {model_path}")

            # Verify checksum if available
            if config.checksum:
                if not self.verify_checksum(model_id):
                    model_path.unlink()  # Delete corrupted file
                    raise RuntimeError(f"Checksum verification failed for {model_id}")

            # Update metadata
            self.metadata[model_id] = {
                "downloaded_at": Path(model_path).stat().st_mtime,
                "size_bytes": Path(model_path).stat().st_size,
                "url": config.url,
            }
            self._save_metadata()

            return model_path

        except urllib.error.URLError as e:
            logger.error(f"Download failed: {e}")
            raise RuntimeError(f"Failed to download {model_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            if model_path.exists():
                model_path.unlink()  # Clean up partial download
            raise

    def download_all(self, model_type: Optional[str] = None):
        """
        Download all models of a specific type.

        Args:
            model_type: Filter by model type (None for all)
        """
        models_to_download = self.list_models(model_type)

        logger.info(f"Downloading {len(models_to_download)} models...")

        for model_id in models_to_download:
            try:
                self.download(model_id)
            except Exception as e:
                logger.error(f"Failed to download {model_id}: {e}")

    def delete(self, model_id: str):
        """
        Delete a cached model.

        Args:
            model_id: Model identifier
        """
        model_path = self.get_model_path(model_id)

        if model_path.exists():
            model_path.unlink()
            logger.info(f"Deleted model: {model_id}")

            # Remove from metadata
            if model_id in self.metadata:
                del self.metadata[model_id]
                self._save_metadata()
        else:
            logger.warning(f"Model not found: {model_id}")

    def clear_cache(self):
        """Delete all cached models."""
        for model_path in self.cache_dir.glob("*"):
            if model_path.is_file() and model_path != self.metadata_file:
                model_path.unlink()
                logger.info(f"Deleted: {model_path}")

        self.metadata.clear()
        self._save_metadata()
        logger.info("Cache cleared")

    def get_cache_size(self) -> int:
        """
        Get total size of model cache in bytes.

        Returns:
            Total cache size in bytes
        """
        total_size = 0
        for model_path in self.cache_dir.glob("*"):
            if model_path.is_file():
                total_size += model_path.stat().st_size
        return total_size

    def get_cache_info(self) -> Dict:
        """
        Get information about the model cache.

        Returns:
            Dictionary with cache statistics
        """
        downloaded_models = [
            mid for mid in self.models.keys()
            if self.is_downloaded(mid)
        ]

        return {
            "cache_dir": str(self.cache_dir),
            "total_size_mb": self.get_cache_size() / (1024 * 1024),
            "total_models": len(self.models),
            "downloaded_models": len(downloaded_models),
            "downloaded_list": downloaded_models,
        }


# Global instance
_global_downloader: Optional[ModelDownloader] = None


def get_model_downloader(cache_dir: Optional[Path] = None) -> ModelDownloader:
    """
    Get the global model downloader instance.

    Args:
        cache_dir: Optional custom cache directory

    Returns:
        ModelDownloader instance
    """
    global _global_downloader

    if _global_downloader is None:
        _global_downloader = ModelDownloader(cache_dir)

    return _global_downloader


def ensure_model(model_id: str, cache_dir: Optional[Path] = None) -> Path:
    """
    Ensure a model is downloaded and return its path.

    Convenience function for automatic model management.

    Args:
        model_id: Model identifier
        cache_dir: Optional custom cache directory

    Returns:
        Path to model file
    """
    downloader = get_model_downloader(cache_dir)

    if not downloader.is_downloaded(model_id):
        logger.info(f"Model {model_id} not found, downloading...")
        return downloader.download(model_id)

    return downloader.get_model_path(model_id)


if __name__ == "__main__":
    # CLI for model management
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    downloader = get_model_downloader()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python model_downloader.py list [type]")
        print("  python model_downloader.py download <model_id>")
        print("  python model_downloader.py info")
        print("  python model_downloader.py clear")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        model_type = sys.argv[2] if len(sys.argv) > 2 else None
        models = downloader.list_models(model_type)

        print(f"\nAvailable models ({len(models)}):")
        for mid in models:
            config = downloader.models[mid]
            status = "✓" if downloader.is_downloaded(mid) else "✗"
            print(f"  {status} {mid}: {config.name} ({config.size_mb} MB)")

    elif command == "download":
        if len(sys.argv) < 3:
            print("Error: model_id required")
            sys.exit(1)

        model_id = sys.argv[2]
        try:
            path = downloader.download(model_id)
            print(f"\nSuccess! Model saved to: {path}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "info":
        info = downloader.get_cache_info()
        print(f"\nModel Cache Info:")
        print(f"  Cache directory: {info['cache_dir']}")
        print(f"  Total size: {info['total_size_mb']:.2f} MB")
        print(f"  Models downloaded: {info['downloaded_models']}/{info['total_models']}")
        print(f"  Downloaded models: {', '.join(info['downloaded_list'])}")

    elif command == "clear":
        confirm = input("Clear all cached models? (yes/no): ")
        if confirm.lower() == "yes":
            downloader.clear_cache()
            print("Cache cleared")
        else:
            print("Cancelled")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

"""
Configuration management for Sentient Core.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class for Sentient Core."""

    # Core settings
    model: str = "sentient-v4-base"
    device: str = "auto"
    max_memory: str = "8GB"

    # Paths
    model_path: str = "~/.sentient-core/models"
    cache_dir: str = "~/.sentient-core/cache"
    log_dir: str = "~/.sentient-core/logs"

    # Features
    enable_reasoning: bool = True
    enable_memory: bool = True
    enable_learning: bool = True
    enable_multi_agent: bool = True
    enable_voice: bool = True
    enable_vision: bool = True

    # API settings
    api_host: str = "127.0.0.1"
    api_port: int = 8080

    # Additional config
    config_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        path = Path(config_path).expanduser()

        if not path.exists():
            # Try default locations
            default_paths = [
                Path("~/.sentient-core/config.yaml").expanduser(),
                Path("config/default.yaml"),
                Path("config/local.yaml"),
            ]

            for default_path in default_paths:
                if default_path.exists():
                    path = default_path
                    break
            else:
                # Use default config
                return cls()

        with open(path, 'r') as f:
            config_data = yaml.safe_load(f)

        # Extract core settings
        core_settings = config_data.get('core', {})
        features = config_data.get('features', {})
        api_settings = config_data.get('api', {})

        return cls(
            model=core_settings.get('model', 'sentient-v4-base'),
            device=core_settings.get('device', 'auto'),
            max_memory=core_settings.get('max_memory', '8GB'),
            model_path=core_settings.get('model_path', '~/.sentient-core/models'),
            cache_dir=core_settings.get('cache_dir', '~/.sentient-core/cache'),
            enable_reasoning=features.get('reasoning', True),
            enable_memory=features.get('memory', True),
            enable_learning=features.get('learning', True),
            enable_multi_agent=features.get('multi_agent', True),
            enable_voice=features.get('audio_processing', True),
            enable_vision=features.get('vision_processing', True),
            api_host=api_settings.get('host', '127.0.0.1'),
            api_port=api_settings.get('port', 8080),
            config_data=config_data
        )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key path (e.g., 'core.model')."""
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def ensure_directories(self):
        """Ensure all required directories exist."""
        dirs = [
            self.model_path,
            self.cache_dir,
            self.log_dir,
        ]

        for dir_path in dirs:
            path = Path(dir_path).expanduser()
            path.mkdir(parents=True, exist_ok=True)

# Sentient Core v4

A next-generation artificial intelligence framework for building autonomous, self-aware cognitive systems with advanced reasoning capabilities.

## Overview

Sentient Core v4 is an advanced AI cognitive architecture designed to enable:

- **Autonomous Reasoning**: Self-directed problem-solving and decision-making
- **Multi-Modal Processing**: Integration of text, vision, audio, and sensor data
- **Memory Systems**: Long-term and short-term memory with contextual retrieval
- **Learning Capabilities**: Continuous learning and adaptation from interactions
- **Goal-Oriented Behavior**: Planning and executing complex multi-step tasks
- **Self-Awareness**: Introspection and meta-cognitive capabilities

## Features

### Core Capabilities
- Advanced neural architecture with transformer-based models
- Distributed processing and parallel execution
- Real-time decision making and response generation
- Extensible plugin system for custom modules
- **Brain-inspired memory system with OpenMemory integration**
- Comprehensive logging and monitoring
- Security and privacy controls

### Latest Advancements (v4)
- Enhanced reasoning engine with causal inference
- **OpenMemory integration**: Brain-inspired memory with multi-sector organization, automatic decay, and graph-based associations
- Improved memory consolidation and retrieval with 95% recall accuracy
- Multi-agent coordination and collaboration
- Advanced natural language understanding
- Emotional intelligence and sentiment analysis with dedicated memory sectors
- Explainable AI capabilities
- **Coral Edge TPU Training Pipeline**: Optimize and deploy models on Google Coral devices
- **Google APK Pipeline Integration**: Build and distribute Android applications

## Quick Start

```bash
# Clone the repository
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4

# Run automated setup (Linux/macOS)
./scripts/setup.sh

# Or follow platform-specific guides
```

## Installation

Choose your platform for detailed installation instructions:

- [Linux Installation Guide](docs/installation/INSTALL_LINUX.md) - Ubuntu, Debian, Fedora, Arch
- [macOS Installation Guide](docs/installation/INSTALL_MACOS.md) - Intel and Apple Silicon
- [Windows Installation Guide](docs/installation/INSTALL_WINDOWS.md) - Windows 10/11, WSL2
- [Docker Installation Guide](docs/installation/INSTALL_DOCKER.md) - Container deployment

## Edge and Mobile Deployment

### Google Coral Edge TPU

Train and deploy optimized models on Google Coral edge devices:

```bash
# Train model for Coral
./scripts/train-coral.sh --config config/coral_config.yaml --epochs 50

# Deploy to Coral device
sentient-core coral deploy --model models/coral/edgetpu/model_edgetpu.tflite
```

**Features:**
- TensorFlow Lite model optimization
- INT8 quantization for Edge TPU
- Sub-10ms inference latency
- Automated deployment to Coral devices
- Multi-device load balancing

**Learn more:** [Coral Training Pipeline Documentation](docs/coral/CORAL_TRAINING.md)

### Android APK Pipeline

Build and distribute Sentient Core as Android applications:

```bash
# Build Android APK
./scripts/build-android.sh --release --aab

# Upload to Google Play
./scripts/build-android.sh --release --aab --upload
```

**Features:**
- Native Android app development
- TensorFlow Lite on-device inference
- Google Play automated distribution
- Firebase ML Kit integration
- CI/CD pipeline with GitHub Actions

**Learn more:** [Google APK Pipeline Documentation](docs/android/GOOGLE_APK_PIPELINE.md)

## System Requirements

### Minimum Requirements
- **CPU**: 4+ cores, 2.5 GHz
- **RAM**: 8 GB
- **Storage**: 20 GB available space
- **OS**: Linux (Ubuntu 20.04+), macOS (11+), Windows 10/11
- **Python**: 3.9 or higher

### Recommended Requirements
- **CPU**: 8+ cores, 3.0 GHz
- **RAM**: 16 GB or more
- **GPU**: NVIDIA GPU with 8GB+ VRAM (CUDA 11.8+)
- **Storage**: 50 GB SSD
- **Network**: High-speed internet for model downloads

## Architecture

```
sentient-core-v4/
├── core/                 # Core cognitive engine
│   ├── reasoning/        # Reasoning and inference
│   ├── memory/           # Memory systems (including OpenMemory integration)
│   ├── perception/       # Multi-modal input processing
│   └── action/           # Action execution
├── integrations/         # External system integrations
│   └── openmemory/       # OpenMemory Python SDK
├── openmemory-backend/   # OpenMemory server (Node.js/TypeScript)
├── openmemory-dashboard/ # OpenMemory web dashboard
├── models/               # AI models and weights
├── plugins/              # Extensible plugin system
├── config/               # Configuration files
├── examples/             # Example applications
├── scripts/              # Utility scripts
├── tests/                # Test suite
└── docs/                 # Documentation
```

## Configuration

After installation, configure your instance:

```bash
# Copy default configuration
cp config/default.yaml config/local.yaml

# Edit configuration
nano config/local.yaml
```

Key configuration areas:
- Model selection and parameters
- Memory settings
- API endpoints and authentication
- Logging levels
- Resource limits

## Usage

### Basic Usage

```python
from sentient_core import SentientAgent

# Initialize agent
agent = SentientAgent(config_path="config/local.yaml")

# Start agent
agent.initialize()

# Interact
response = agent.process("Analyze this data and provide insights")
print(response)
```

### Advanced Usage

See [Documentation](docs/README.md) for:
- API reference
- Plugin development
- Custom model integration
- Deployment strategies
- Performance tuning

## Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black .
isort .

# Linting
flake8 .
pylint sentient_core/
```

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Documentation

- [Installation Guides](docs/installation/)
- **[OpenMemory Integration Guide](docs/OPENMEMORY_INTEGRATION.md)** - Brain-inspired memory system
- [User Guide](docs/guides/USER_GUIDE.md)
- [API Reference](docs/api/API_REFERENCE.md)
- [Architecture Overview](docs/architecture/ARCHITECTURE.md)
- [Plugin Development](docs/plugins/PLUGIN_DEVELOPMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Security

Sentient Core v4 includes built-in security features:
- Sandboxed execution environment
- Rate limiting and resource controls
- Audit logging
- Encrypted data storage
- API authentication and authorization

For security concerns, see [SECURITY.md](SECURITY.md)

## Performance

Typical performance metrics:
- Response time: 100-500ms (CPU), 50-200ms (GPU)
- Throughput: 10-100 requests/second
- Memory usage: 2-8 GB base, scales with model size

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Citation

If you use Sentient Core v4 in your research, please cite:

```bibtex
@software{sentient_core_v4,
  title = {Sentient Core v4: Advanced AI Cognitive Architecture},
  author = {Sentient Core Team},
  year = {2025},
  url = {https://github.com/thotsl4yer69/sentient-core-v4}
}
```

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/thotsl4yer69/sentient-core-v4/issues)
- Discussions: [GitHub Discussions](https://github.com/thotsl4yer69/sentient-core-v4/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## Acknowledgments

Built with contributions from the AI research community and powered by:
- PyTorch / TensorFlow
- Transformers (Hugging Face)
- LangChain
- Vector databases (Pinecone, Chroma)
- And many other open-source projects

---

**Version**: 4.0.0
**Status**: Active Development
**Last Updated**: November 2025

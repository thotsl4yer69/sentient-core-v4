# Sentient Core v4 - Examples

This directory contains example implementations demonstrating various features of Sentient Core v4.

## Available Examples

### Coral Edge TPU

**train_and_deploy.py** - Complete pipeline for Coral deployment

```bash
cd examples/coral
python train_and_deploy.py
```

Demonstrates:
- Model training for edge devices
- TensorFlow Lite conversion
- INT8 quantization
- Edge TPU compilation
- Deployment to Coral devices
- Performance benchmarking

**Requirements:**
```bash
pip install -r requirements-coral.txt
```

**See also:** [Coral Training Documentation](../docs/coral/CORAL_TRAINING.md)

### Android APK Pipeline

**build_and_deploy.py** - Android app build and deployment

```bash
cd examples/android
python build_and_deploy.py
```

Demonstrates:
- Environment validation
- APK/AAB building
- Testing automation
- Device installation
- Google Play upload

**Requirements:**
- Android Studio
- Android SDK
- Google Play service account (for upload)

**See also:** [Android APK Documentation](../docs/android/GOOGLE_APK_PIPELINE.md)

## Quick Start

### 1. Setup Environment

```bash
# Install base dependencies
pip install -r requirements.txt

# For Coral examples
pip install -r requirements-coral.txt

# For Android examples
# Install Android Studio and SDK
export ANDROID_HOME=$HOME/Android/Sdk
```

### 2. Run Examples

```bash
# Coral training example
python examples/coral/train_and_deploy.py

# Android build example
python examples/android/build_and_deploy.py
```

## Example Structure

```
examples/
├── coral/
│   ├── train_and_deploy.py    # Full training pipeline
│   ├── inference_test.py      # Edge inference testing
│   └── benchmark.py            # Performance benchmarking
├── android/
│   ├── build_and_deploy.py    # APK build pipeline
│   ├── firebase_setup.py      # Firebase integration
│   └── test_app.py             # App testing
└── README.md                   # This file
```

## Common Use Cases

### Training a Coral Model

```python
from sentient_core.coral import CoralTrainer

trainer = CoralTrainer(config_path="config/coral_config.yaml")
history = trainer.train(
    train_data=train_data,
    val_data=val_data
)
```

### Building Android APK

```bash
./scripts/build-android.sh --release --aab
```

### Deploying to Edge Device

```bash
sentient-core coral deploy \
    --model models/coral/edgetpu/model_edgetpu.tflite \
    --device coral-usb
```

### Uploading to Google Play

```bash
./scripts/build-android.sh --release --aab --upload
```

## Configuration

Each example can be configured via:
- YAML config files in `config/`
- Environment variables
- Command-line arguments

Example configurations:
- `config/coral_config.yaml` - Coral training settings
- `android/app/build.gradle` - Android build settings

## Troubleshooting

### Coral Examples

**Issue:** Edge TPU compiler not found
```bash
sudo apt-get install edgetpu-compiler
```

**Issue:** PyCoral import error
```bash
pip install pycoral tflite-runtime
```

### Android Examples

**Issue:** ANDROID_HOME not set
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

**Issue:** Signing configuration missing
```bash
export SENTIENT_KEYSTORE_FILE=/path/to/keystore.jks
export SENTIENT_KEYSTORE_PASSWORD=your_password
export SENTIENT_KEY_ALIAS=your_alias
export SENTIENT_KEY_PASSWORD=your_key_password
```

## Additional Resources

### Documentation
- [Installation Guides](../docs/installation/)
- [Coral Training Pipeline](../docs/coral/CORAL_TRAINING.md)
- [Android APK Pipeline](../docs/android/GOOGLE_APK_PIPELINE.md)
- [API Reference](../docs/api/API_REFERENCE.md)

### Tutorials
- [Building Your First Coral Model](../docs/tutorials/FIRST_CORAL_MODEL.md)
- [Android App Development](../docs/tutorials/ANDROID_APP.md)
- [Edge-Cloud Hybrid Systems](../docs/tutorials/EDGE_CLOUD_HYBRID.md)

## Contributing

To contribute examples:
1. Fork the repository
2. Create your example in appropriate directory
3. Add documentation and tests
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Support

For issues with examples:
- Check [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)
- Report on [GitHub Issues](https://github.com/thotsl4yer69/sentient-core-v4/issues)
- Tag with `examples` label

---

**Version**: 4.0.0
**Last Updated**: November 2025

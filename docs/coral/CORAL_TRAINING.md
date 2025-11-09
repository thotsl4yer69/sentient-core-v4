# Coral Training Pipeline

Complete guide for training and deploying Sentient Core v4 models on Google Coral edge devices.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Model Training](#model-training)
- [Model Optimization](#model-optimization)
- [Edge Deployment](#edge-deployment)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)

## Overview

The Coral Training Pipeline enables you to:
- Train models optimized for edge devices
- Convert models to TensorFlow Lite format
- Quantize models for Edge TPU
- Deploy to Google Coral devices
- Run inference on edge with minimal latency

### Supported Devices

- **Coral Dev Board**
- **Coral USB Accelerator**
- **Coral Mini PCIe Accelerator**
- **Coral M.2 Accelerator**
- **Coral PCIe Accelerator**

## Prerequisites

### System Requirements

- **Development Machine**:
  - Python 3.9+
  - TensorFlow 2.13+
  - 16GB+ RAM
  - Ubuntu 20.04+ or Debian 11+

- **Target Device**:
  - Google Coral hardware
  - Mendel OS or compatible Linux
  - 1GB+ RAM

### Software Dependencies

```bash
# Install TensorFlow
pip install tensorflow>=2.13.0

# Install TensorFlow Lite tools
pip install tflite-model-maker
pip install tflite-support

# Install Edge TPU compiler
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
sudo apt-get update
sudo apt-get install edgetpu-compiler

# Install PyCoral (for inference)
sudo apt-get install python3-pycoral
```

## Installation

### Step 1: Install Sentient Core with Coral Support

```bash
cd ~/sentient-core-v4
source venv/bin/activate

# Install Coral-specific dependencies
pip install -r requirements-coral.txt

# Verify installation
python -c "from pycoral.utils import edgetpu; print('PyCoral installed successfully')"
```

### Step 2: Setup Coral Device

#### For Coral Dev Board

```bash
# Connect via serial or SSH
ssh mendel@192.168.100.2  # Default IP

# Update system
sudo apt-get update
sudo apt-get upgrade

# Install Edge TPU runtime
sudo apt-get install libedgetpu1-std
```

#### For Coral USB Accelerator

```bash
# Install USB rules
echo "SUBSYSTEM==\"usb\", ATTRS{idVendor}=\"1a6e\", GROUP=\"plugdev\"" | sudo tee /etc/udev/rules.d/99-edgetpu-accelerator.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Model Training

### Step 1: Prepare Training Data

```python
from sentient_core.coral import CoralDataset

# Load and prepare dataset
dataset = CoralDataset(
    data_dir="data/training",
    image_size=(224, 224),
    batch_size=32
)

# Split data
train_data, val_data, test_data = dataset.split(
    train_ratio=0.8,
    val_ratio=0.1,
    test_ratio=0.1
)
```

### Step 2: Configure Training Pipeline

```yaml
# coral_config.yaml
training:
  model_type: "mobilenet_v2"  # Optimized for edge
  input_shape: [224, 224, 3]
  num_classes: 10

  optimizer:
    type: "adam"
    learning_rate: 0.001

  training:
    epochs: 50
    batch_size: 32
    early_stopping:
      patience: 5
      min_delta: 0.001

  quantization:
    enabled: true
    type: "int8"  # Required for Edge TPU

  edge_tpu:
    compile: true
    num_inferences: 100  # For calibration
```

### Step 3: Train Model

```python
from sentient_core.coral import CoralTrainer

# Initialize trainer
trainer = CoralTrainer(config_path="coral_config.yaml")

# Train model
history = trainer.train(
    train_data=train_data,
    val_data=val_data,
    save_path="models/coral"
)

# Evaluate
metrics = trainer.evaluate(test_data)
print(f"Accuracy: {metrics['accuracy']:.4f}")
```

### Step 4: Command-Line Training

```bash
# Train using CLI
sentient-core coral train \
    --config coral_config.yaml \
    --data-dir data/training \
    --output-dir models/coral \
    --epochs 50 \
    --batch-size 32 \
    --quantize int8

# Monitor training
tensorboard --logdir models/coral/logs
```

## Model Optimization

### Quantization

#### Post-Training Quantization

```python
from sentient_core.coral import ModelOptimizer

optimizer = ModelOptimizer()

# Full integer quantization (required for Edge TPU)
optimized_model = optimizer.quantize(
    model_path="models/coral/model.h5",
    quantization_type="int8",
    representative_dataset=train_data,
    output_path="models/coral/model_quantized.tflite"
)
```

#### Quantization-Aware Training

```python
import tensorflow_model_optimization as tfmot

# Apply quantization during training
quantize_model = tfmot.quantization.keras.quantize_model

q_aware_model = quantize_model(base_model)

# Train quantized model
q_aware_model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

q_aware_model.fit(train_data, validation_data=val_data, epochs=50)
```

### Convert to TensorFlow Lite

```python
from sentient_core.coral import TFLiteConverter

converter = TFLiteConverter()

# Convert to TFLite with optimization
tflite_model = converter.convert(
    model_path="models/coral/model.h5",
    optimization="default",
    target_spec={
        "supported_ops": ["TFLITE_BUILTINS_INT8"],
        "supported_types": ["int8"]
    }
)

# Save TFLite model
converter.save(tflite_model, "models/coral/model.tflite")
```

### Compile for Edge TPU

```bash
# Compile TFLite model for Edge TPU
edgetpu_compiler models/coral/model.tflite \
    --out_dir models/coral/edgetpu

# Verify compilation
ls -lh models/coral/edgetpu/
# Should see model_edgetpu.tflite
```

#### Using Python

```python
from sentient_core.coral import EdgeTPUCompiler

compiler = EdgeTPUCompiler()

# Compile model
edgetpu_model = compiler.compile(
    tflite_path="models/coral/model.tflite",
    output_dir="models/coral/edgetpu"
)

# Check compilation report
print(compiler.get_report())
```

## Edge Deployment

### Deploy to Coral Device

#### Method 1: SCP Transfer

```bash
# Copy model to Coral device
scp models/coral/edgetpu/model_edgetpu.tflite mendel@192.168.100.2:/home/mendel/models/

# Copy inference script
scp scripts/coral_inference.py mendel@192.168.100.2:/home/mendel/
```

#### Method 2: Using Deployment Script

```bash
# Deploy using automation script
sentient-core coral deploy \
    --model models/coral/edgetpu/model_edgetpu.tflite \
    --device coral-dev-board \
    --host 192.168.100.2 \
    --user mendel
```

### Run Inference on Coral

```python
# On Coral device
from pycoral.adapters import common
from pycoral.adapters import classify
from pycoral.utils.edgetpu import make_interpreter
from PIL import Image

# Load model
interpreter = make_interpreter('models/model_edgetpu.tflite')
interpreter.allocate_tensors()

# Load and preprocess image
image = Image.open('test_image.jpg')
image = image.resize((224, 224))

# Set input
common.set_input(interpreter, image)

# Run inference
interpreter.invoke()

# Get results
classes = classify.get_classes(interpreter, top_k=5)
for c in classes:
    print(f'{c.id}: {c.score:.4f}')
```

### Benchmark Performance

```bash
# On Coral device
python3 /usr/share/edgetpu/examples/model_benchmark.py \
    --model models/model_edgetpu.tflite \
    --iterations 1000

# Expected output:
# Average inference time: 2-5ms
# Throughput: 200-500 FPS
```

## Integration with Sentient Core

### Real-Time Edge Inference

```python
from sentient_core.coral import CoralAgent

# Initialize edge agent
agent = CoralAgent(
    model_path="models/coral/edgetpu/model_edgetpu.tflite",
    device="usb:0"  # or "pci:0" for PCIe
)

# Run inference
result = agent.inference(
    input_data=image,
    return_embeddings=True
)

print(f"Prediction: {result.prediction}")
print(f"Confidence: {result.confidence}")
print(f"Latency: {result.latency_ms}ms")
```

### Multi-Device Deployment

```python
from sentient_core.coral import MultiCoralManager

# Manage multiple Coral devices
manager = MultiCoralManager()

# Auto-detect devices
devices = manager.detect_devices()
print(f"Found {len(devices)} Coral devices")

# Load balance across devices
manager.load_model("models/coral/edgetpu/model_edgetpu.tflite")

# Process batch
results = manager.inference_batch(
    images=image_batch,
    strategy="round_robin"  # or "load_balance"
)
```

### Edge-Cloud Hybrid

```python
from sentient_core.coral import HybridInference

# Hybrid processing
hybrid = HybridInference(
    edge_model="models/coral/edgetpu/model_edgetpu.tflite",
    cloud_model="models/full/model.h5",
    threshold=0.8  # Use cloud if confidence < 0.8
)

# Automatic routing
result = hybrid.predict(image)
print(f"Processed on: {result.device}")  # 'edge' or 'cloud'
```

## Performance Tuning

### Optimize Input Pipeline

```python
from sentient_core.coral import InputPipeline

pipeline = InputPipeline(
    input_shape=(224, 224, 3),
    preprocessing="mobilenet_v2",
    use_cache=True,
    num_parallel_calls=4
)

# Process images efficiently
processed_images = pipeline.process_batch(image_paths)
```

### Model Architecture Selection

```yaml
# Best architectures for Coral
architectures:
  - MobileNetV2 (Recommended)
  - MobileNetV3
  - EfficientNet-Lite
  - SqueezeNet
  - ShuffleNet

# Avoid:
  - ResNet (too heavy)
  - VGG (too slow)
  - Inception (not optimized)
```

### Batch Inference

```python
# Batch processing for throughput
from sentient_core.coral import BatchInference

batch_inference = BatchInference(
    model_path="models/coral/edgetpu/model_edgetpu.tflite",
    batch_size=8  # Process 8 images at once
)

# Process efficiently
results = batch_inference.process(image_batch)
```

## Advanced Features

### On-Device Fine-Tuning

```python
from sentient_core.coral import OnDeviceLearning

# Enable on-device learning
learner = OnDeviceLearning(
    base_model="models/coral/edgetpu/model_edgetpu.tflite",
    learning_rate=0.0001
)

# Update model with new data
learner.update(new_samples, new_labels)

# Save updated model
learner.save("models/coral/updated_model.tflite")
```

### Model Compression

```python
from sentient_core.coral import ModelCompressor

compressor = ModelCompressor()

# Apply compression techniques
compressed_model = compressor.compress(
    model_path="models/coral/model.h5",
    techniques=["pruning", "quantization", "knowledge_distillation"],
    target_size_mb=5
)
```

### Multi-Model Pipeline

```python
from sentient_core.coral import ModelPipeline

# Create detection + classification pipeline
pipeline = ModelPipeline([
    {
        "name": "detector",
        "model": "models/coral/detector_edgetpu.tflite",
        "type": "object_detection"
    },
    {
        "name": "classifier",
        "model": "models/coral/classifier_edgetpu.tflite",
        "type": "classification"
    }
])

# Run pipeline
results = pipeline.run(image)
```

## Monitoring and Logging

### Performance Monitoring

```python
from sentient_core.coral import PerformanceMonitor

monitor = PerformanceMonitor()

# Track metrics
monitor.start()
result = agent.inference(image)
metrics = monitor.stop()

print(f"Inference time: {metrics.inference_ms}ms")
print(f"Preprocessing: {metrics.preprocess_ms}ms")
print(f"Postprocessing: {metrics.postprocess_ms}ms")
print(f"Total: {metrics.total_ms}ms")
```

### Edge Logging

```python
from sentient_core.coral import EdgeLogger

logger = EdgeLogger(
    log_level="INFO",
    log_file="/var/log/sentient-coral.log",
    max_size_mb=100
)

logger.info("Model loaded successfully")
logger.metric("inference_time", 3.2)
```

## Troubleshooting

### Model Not Compiling

```bash
# Check model compatibility
edgetpu_compiler --show_operations models/coral/model.tflite

# Common issues:
# 1. Non-quantized model - Must be fully quantized to int8
# 2. Unsupported operations - Use supported ops only
# 3. Dynamic shapes - Use fixed input shapes
```

### Poor Performance

```python
# Profile model
from sentient_core.coral import ModelProfiler

profiler = ModelProfiler()
report = profiler.profile("models/coral/edgetpu/model_edgetpu.tflite")

print(report.bottlenecks)
print(report.recommendations)
```

### Device Not Detected

```bash
# Check device connection
lsusb | grep "Global Unichip"

# Check Edge TPU runtime
ls /dev/apex_0

# Reinstall runtime if needed
sudo apt-get install --reinstall libedgetpu1-std
```

### Memory Issues

```yaml
# Reduce model size in config
model:
  architecture: "mobilenet_v2"
  width_multiplier: 0.75  # Reduce from 1.0
  input_size: 192  # Reduce from 224
```

## Best Practices

### Model Design

1. **Use Mobile-Optimized Architectures**: MobileNetV2, EfficientNet-Lite
2. **Keep Models Small**: Target < 10MB for best performance
3. **Use Depthwise Separable Convolutions**: Better efficiency
4. **Limit Model Depth**: Fewer layers = faster inference

### Quantization

1. **Always Use Int8 Quantization**: Required for Edge TPU
2. **Provide Representative Data**: For calibration
3. **Test Accuracy After Quantization**: Ensure < 1% loss
4. **Use Quantization-Aware Training**: For best results

### Deployment

1. **Benchmark Before Deployment**: Test on target hardware
2. **Monitor Performance**: Track inference times
3. **Version Control Models**: Track model versions
4. **Plan for Updates**: OTA update strategy

## Example Projects

### Image Classification

```bash
# Train classification model
sentient-core coral train-classifier \
    --data data/images \
    --classes 10 \
    --architecture mobilenet_v2 \
    --epochs 50
```

### Object Detection

```bash
# Train detector
sentient-core coral train-detector \
    --data data/coco \
    --architecture ssd_mobilenet_v2 \
    --epochs 100
```

### Segmentation

```bash
# Train segmentation model
sentient-core coral train-segmentation \
    --data data/cityscapes \
    --architecture deeplabv3_mobilenet \
    --epochs 75
```

## Performance Benchmarks

| Model | Size | Latency (USB) | Latency (PCIe) | Accuracy |
|-------|------|---------------|----------------|----------|
| MobileNetV2 | 3.5MB | 3.2ms | 1.8ms | 71.8% |
| MobileNetV3 | 2.9MB | 2.8ms | 1.5ms | 75.2% |
| EfficientNet-Lite0 | 4.2MB | 4.1ms | 2.3ms | 77.1% |

## Resources

### Documentation

- [Google Coral Docs](https://coral.ai/docs/)
- [Edge TPU Compiler](https://coral.ai/docs/edgetpu/compiler/)
- [PyCoral API](https://coral.ai/docs/reference/py/)

### Tools

- [Model Zoo](https://coral.ai/models/)
- [TensorFlow Lite](https://www.tensorflow.org/lite)
- [Model Optimization Toolkit](https://www.tensorflow.org/model_optimization)

### Community

- [Coral Community](https://coral.ai/community/)
- [GitHub Issues](https://github.com/google-coral/edgetpu/issues)

## Next Steps

- [Android APK Integration](GOOGLE_APK_PIPELINE.md)
- [Edge Device Management](../guides/EDGE_MANAGEMENT.md)
- [IoT Deployment](../guides/IOT_DEPLOYMENT.md)

---

**Version**: 4.0.0
**Last Updated**: November 2025
**Maintained by**: Sentient Core Team

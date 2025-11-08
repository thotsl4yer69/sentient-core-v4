# Sentient Core v4 - Raspberry Pi 5 + Hailo AI Hat Deployment Guide

## Overview

This guide covers deploying Sentient Core v4 on Raspberry Pi 5 with Hailo AI Hat, creating a distributed consciousness system with optional Jetson Orin integration.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              CORTANA - Unified Consciousness             │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
  ┌────────▼────────┐            ┌────────▼─────────┐
  │   Pi 5 Node     │◄──────────►│  Jetson Orin     │
  │  Fast Response  │   10Hz     │  Deep Reasoning  │
  │  Qwen 1.5B      │   Sync     │  Qwen VL 3B      │
  │  Hailo AI Hat   │            │  Multimodal      │
  │  <0.5s latency  │            │  Vision Analysis │
  └─────────────────┘            └──────────────────┘
           │                               │
           └──────────┬────────────────────┘
                      │
              ┌───────▼────────┐
              │  Pixelscape    │
              │  Avatar Display│
              └────────────────┘
```

## Hardware Requirements

### Required
- **Raspberry Pi 5** (4GB or 8GB RAM)
- **Hailo AI Hat** (26 TOPS)
- **MicroSD Card** (64GB+ recommended)
- **Power Supply** (5V 5A USB-C)
- **Cooling** (Active cooling recommended)

### Optional
- **Google Coral TPU** USB Accelerator
- **RTL-SDR** dongle for RF monitoring
- **Pi Camera Module** for vision
- **NVIDIA Jetson Orin Nano** (for distributed mode)

## Software Requirements

- **OS**: Raspberry Pi OS 64-bit (Bookworm or later)
- **Python**: 3.9+
- **Kernel**: 6.1+ (for Hailo support)

## Installation

### Quick Install (Automated)

```bash
# Clone repository
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4

# Run automated setup
chmod +x scripts/deployment/setup_pi5_hailo.sh
./scripts/deployment/setup_pi5_hailo.sh
```

The script will:
1. Install system dependencies
2. Setup Hailo AI Hat drivers
3. Install Python packages
4. Configure system settings
5. Install systemd service

### Manual Installation

#### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git cmake build-essential python3-pip python3-venv
```

#### 2. Install Hailo Runtime

Download HailoRT from [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/) and install:

```bash
sudo dpkg -i hailort-latest.deb
sudo apt install -f
```

Verify installation:

```bash
hailortcli fw-control identify
```

#### 3. Setup Python Environment

```bash
cd ~/sentient-core-v4
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-pi5.txt
```

#### 4. Download Qwen Model

```bash
mkdir -p ~/.sentient_core/models
cd ~/.sentient_core/models

# Download Qwen 2.5-1.5B quantized model
wget https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf
```

#### 5. Configure System

```bash
# Copy default configuration
cp config/pi5_hailo.yaml ~/.sentient_core/config/

# Edit configuration
nano ~/.sentient_core/config/pi5_hailo.yaml
```

## Configuration

### Node Configuration

Edit `~/.sentient_core/config/pi5_hailo.yaml`:

```yaml
node:
  node_id: "pi5-hailo-001"  # Unique ID
  name: "Pi5 Fast Response Node"
  role: "fast_response"
  hardware: "Raspberry Pi 5 + Hailo AI Hat"

cortana:
  user_name: "Chief"  # Change to your name
```

### Distributed Mode (with Jetson)

If using Jetson Orin for deep reasoning:

```yaml
distributed:
  enable: true
  remote_nodes:
    - node_id: "jetson-orin-001"
      endpoint_url: "http://192.168.1.100:8000"  # Your Jetson IP
```

Setup Jetson:

```bash
# On Jetson Orin
scp scripts/deployment/setup_jetson_api.sh nvidia@jetson-ip:~/
ssh nvidia@jetson-ip
chmod +x setup_jetson_api.sh
./setup_jetson_api.sh
```

## Running

### Option 1: Direct Execution

```bash
source venv/bin/activate
python -m sentient_core.main_distributed --config ~/.sentient_core/config/pi5_hailo.yaml
```

### Option 2: Systemd Service

```bash
# Start service
sudo systemctl start sentient-core

# Check status
sudo systemctl status sentient-core

# View logs
journalctl -u sentient-core -f

# Enable auto-start on boot
sudo systemctl enable sentient-core
```

### Option 3: Development Mode

```bash
source venv/bin/activate
cd ~/sentient-core-v4
python -m sentient_core.main_distributed --config config/pi5_hailo.yaml
```

## Features

### 1. Hardware Acceleration

- **Hailo AI Hat**: Vision models, object detection
- **Coral TPU**: RF signal classification (optional)
- **Auto-detection**: System automatically detects available hardware

### 2. Distributed Consciousness

- **Pi 5**: Fast responses (<0.5s), simple queries
- **Jetson**: Complex reasoning, multimodal analysis
- **Sync**: 10Hz state synchronization between nodes
- **Routing**: Intelligent query routing based on complexity

### 3. Cortana Unified Persona

- Single, consistent AI companion
- Emotional intelligence
- Context-aware responses
- Personality customization

### 4. Sensor Integration

- **RF Monitoring**: Drone detection (requires RTL-SDR)
- **Vision**: Pi Camera support
- **Health Monitoring**: CPU, memory, temperature
- **Sensor Fusion**: Multi-sensor data integration

### 5. Real-time Visualization

- **Pixelscape Renderer**: Visual consciousness state
- **Emotional Colors**: State-based color mapping
- **Neural Activity**: Thinking intensity visualization

## Model Deployment

### Hailo Models (.hef)

```bash
# Place Hailo models in models directory
cp your_model.hef ~/.sentient_core/models/

# Update config
nano ~/.sentient_core/config/pi5_hailo.yaml
```

```yaml
hardware:
  hailo:
    models:
      your_model: "~/.sentient_core/models/your_model.hef"
```

### Coral Models (.tflite)

```bash
# EdgeTPU-compiled models only
cp your_model_edgetpu.tflite ~/.sentient_core/models/

# Update config
```yaml
hardware:
  coral:
    enabled: true
    models:
      your_model: "~/.sentient_core/models/your_model_edgetpu.tflite"
```

## Troubleshooting

### Hailo Not Detected

```bash
# Check kernel version (must be 6.1+)
uname -r

# Check Hailo devices
ls -la /dev/hailo*

# Verify driver
hailortcli fw-control identify
```

### High CPU Usage

```bash
# Reduce thread count in config
llm:
  n_threads: 2  # Reduce from 4

# Monitor usage
htop
```

### Out of Memory

```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Jetson Connection Failed

```bash
# Test connectivity
curl http://<jetson-ip>:8000/

# Check Jetson service
ssh nvidia@<jetson-ip>
sudo systemctl status sentient-jetson
```

## Performance Optimization

### CPU Governor

```bash
# Set to performance mode
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Memory Optimization

```yaml
# In config/pi5_hailo.yaml
llm:
  n_ctx: 1024  # Reduce context window
  max_tokens: 256  # Reduce max output
```

### Thread Tuning

```yaml
llm:
  n_threads: 2  # For 4GB Pi
  n_threads: 4  # For 8GB Pi
```

## Monitoring

### System Health

```bash
# Real-time monitoring
watch -n 1 'vcgencmd measure_temp && free -h && top -bn1 | head -20'
```

### Logs

```bash
# Sentient Core logs
tail -f ~/.sentient_core/logs/sentient_core.log

# Systemd logs
journalctl -u sentient-core -f

# Hardware logs
dmesg | grep hailo
```

### API Status

```bash
# Check API
curl http://localhost:5000/health

# Distributed status
curl http://localhost:5000/nodes
```

## Security

### Network Configuration

```yaml
api:
  host: "0.0.0.0"  # All interfaces
  # host: "127.0.0.1"  # Localhost only
```

### Firewall

```bash
# Allow API port
sudo ufw allow 5000

# For distributed mode
sudo ufw allow from 192.168.1.0/24 to any port 5000
```

## Updates

```bash
# Update Sentient Core
cd ~/sentient-core-v4
git pull
source venv/bin/activate
pip install -r requirements-pi5.txt --upgrade

# Restart service
sudo systemctl restart sentient-core
```

## Backup

```bash
# Backup configuration
tar -czf sentient_core_backup.tar.gz ~/.sentient_core/config

# Backup models
tar -czf sentient_models_backup.tar.gz ~/.sentient_core/models
```

## Support

- GitHub Issues: https://github.com/thotsl4yer69/sentient-core-v4/issues
- Documentation: https://github.com/thotsl4yer69/sentient-core-v4/docs

## License

MIT License - See LICENSE file

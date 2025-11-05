# Sentient Core v4 - Linux Installation Guide

Complete installation guide for Linux distributions including Ubuntu, Debian, Fedora, Arch Linux, and others.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Ubuntu / Debian Installation](#ubuntu--debian-installation)
- [Fedora / RHEL / CentOS Installation](#fedora--rhel--centos-installation)
- [Arch Linux Installation](#arch-linux-installation)
- [GPU Support (NVIDIA)](#gpu-support-nvidia)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Linux kernel 5.4 or higher
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8 GB minimum (16+ GB recommended)
- **Storage**: 20 GB free space (50+ GB recommended)
- **Python**: 3.9, 3.10, or 3.11

### Required Permissions

You'll need sudo access for system package installation.

## Ubuntu / Debian Installation

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install System Dependencies

```bash
sudo apt install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3-venv \
    build-essential \
    git \
    curl \
    wget \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev \
    portaudio19-dev \
    ffmpeg
```

### Step 3: Clone Repository

```bash
cd ~
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4
```

### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Upgrade pip and Install Build Tools

```bash
pip install --upgrade pip setuptools wheel
```

### Step 6: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 7: Install Sentient Core

```bash
pip install -e .
```

### Step 8: Initialize Configuration

```bash
mkdir -p ~/.sentient-core
cp config/default.yaml ~/.sentient-core/config.yaml
```

### Step 9: Verify Installation

```bash
sentient-core --version
sentient-core --check-system
```

## Fedora / RHEL / CentOS Installation

### Step 1: Update System

```bash
sudo dnf update -y
```

### Step 2: Install System Dependencies

#### Fedora

```bash
sudo dnf install -y \
    python3.10 \
    python3-devel \
    python3-pip \
    gcc \
    gcc-c++ \
    make \
    git \
    curl \
    wget \
    openssl-devel \
    libffi-devel \
    bzip2-devel \
    readline-devel \
    sqlite-devel \
    ncurses-devel \
    xz-devel \
    tk-devel \
    libxml2-devel \
    xmlsec1-devel \
    portaudio-devel \
    ffmpeg
```

#### RHEL / CentOS (Enable EPEL)

```bash
sudo dnf install -y epel-release
sudo dnf config-manager --set-enabled powertools  # CentOS 8
sudo dnf install -y python3.10 python3-devel gcc git
```

### Step 3: Follow Ubuntu Steps 3-9

Continue with steps 3-9 from the Ubuntu installation guide above.

## Arch Linux Installation

### Step 1: Update System

```bash
sudo pacman -Syu
```

### Step 2: Install System Dependencies

```bash
sudo pacman -S --needed \
    python \
    python-pip \
    base-devel \
    git \
    curl \
    wget \
    openssl \
    libffi \
    bzip2 \
    readline \
    sqlite \
    ncurses \
    xz \
    tk \
    libxml2 \
    xmlsec \
    portaudio \
    ffmpeg
```

### Step 3: Follow Ubuntu Steps 3-9

Continue with steps 3-9 from the Ubuntu installation guide above.

## GPU Support (NVIDIA)

For accelerated performance with NVIDIA GPUs:

### Step 1: Install NVIDIA Drivers

#### Ubuntu / Debian

```bash
# Check for GPU
lspci | grep -i nvidia

# Install drivers
sudo apt install -y nvidia-driver-535

# Reboot
sudo reboot
```

#### Fedora

```bash
sudo dnf install -y akmod-nvidia
sudo reboot
```

#### Arch Linux

```bash
sudo pacman -S nvidia nvidia-utils
sudo reboot
```

### Step 2: Install CUDA Toolkit

#### Ubuntu / Debian

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-3
```

#### Fedora

```bash
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/fedora37/x86_64/cuda-fedora37.repo
sudo dnf install -y cuda-toolkit-12-3
```

### Step 3: Install PyTorch with CUDA Support

```bash
source venv/bin/activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 4: Verify GPU Detection

```bash
sentient-core --check-gpu
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

## Automated Installation

Use the automated setup script for quick installation:

```bash
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The script will:
- Detect your Linux distribution
- Install required dependencies
- Set up Python virtual environment
- Install Sentient Core
- Configure initial settings

## Configuration

### Basic Configuration

Edit your configuration file:

```bash
nano ~/.sentient-core/config.yaml
```

Key settings:

```yaml
# Core settings
core:
  model: "sentient-v4-base"
  device: "cuda"  # or "cpu"
  max_memory: "8GB"

# API settings
api:
  host: "0.0.0.0"
  port: 8080
  auth_required: true

# Logging
logging:
  level: "INFO"
  file: "~/.sentient-core/logs/sentient.log"
```

### Environment Variables

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Sentient Core
export SENTIENT_HOME=~/.sentient-core
export SENTIENT_CONFIG=$SENTIENT_HOME/config.yaml
export SENTIENT_MODELS=$SENTIENT_HOME/models
export PATH=$PATH:~/sentient-core-v4/venv/bin
```

Reload shell:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

## Running Sentient Core

### Start the Service

```bash
# Activate virtual environment
source ~/sentient-core-v4/venv/bin/activate

# Start service
sentient-core start

# Or run in foreground
sentient-core run
```

### As Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/sentient-core.service
```

Add:

```ini
[Unit]
Description=Sentient Core v4 Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/sentient-core-v4
Environment="PATH=/home/youruser/sentient-core-v4/venv/bin"
ExecStart=/home/youruser/sentient-core-v4/venv/bin/sentient-core run
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sentient-core
sudo systemctl start sentient-core
sudo systemctl status sentient-core
```

## Verification

### Check Installation

```bash
# Check version
sentient-core --version

# System check
sentient-core --check-system

# Test inference
sentient-core test --basic
```

### Run Test Suite

```bash
source venv/bin/activate
pytest tests/
```

## Troubleshooting

### Python Version Issues

If python3.10 is not available:

**Ubuntu/Debian:**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER ~/sentient-core-v4

# Fix permissions
chmod +x scripts/*.sh
```

### CUDA Not Found

```bash
# Verify CUDA installation
nvcc --version

# Add to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### Memory Issues

If you encounter out-of-memory errors:

Edit config:
```yaml
core:
  max_memory: "4GB"  # Reduce memory limit
  batch_size: 1      # Reduce batch size
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>

# Or change port in config
```

### Dependencies Conflict

```bash
# Clean installation
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Performance Optimization

### For CPU Systems

```yaml
core:
  device: "cpu"
  threads: 8  # Set to number of CPU cores
  optimization: "performance"
```

### For GPU Systems

```yaml
core:
  device: "cuda"
  mixed_precision: true
  optimization: "gpu"
```

### Disable Unnecessary Features

```yaml
features:
  audio_processing: false
  vision_processing: false
  multi_agent: false
```

## Updating

```bash
cd ~/sentient-core-v4
source venv/bin/activate
git pull origin main
pip install --upgrade -r requirements.txt
sentient-core migrate  # Run any database migrations
```

## Uninstallation

```bash
# Stop service
sudo systemctl stop sentient-core
sudo systemctl disable sentient-core

# Remove files
rm -rf ~/sentient-core-v4
rm -rf ~/.sentient-core
sudo rm /etc/systemd/system/sentient-core.service

# Remove system packages (optional)
sudo apt remove python3.10  # Be careful with this
```

## Next Steps

- [Configuration Guide](../guides/CONFIGURATION.md)
- [User Guide](../guides/USER_GUIDE.md)
- [API Reference](../api/API_REFERENCE.md)
- [Plugin Development](../plugins/PLUGIN_DEVELOPMENT.md)

## Support

For issues specific to Linux installation:
- Check [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Report issues on [GitHub](https://github.com/thotsl4yer69/sentient-core-v4/issues)
- Tag with `linux` and your distribution name

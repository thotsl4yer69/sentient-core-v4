# Sentient Core v4 - macOS Installation Guide

Complete installation guide for macOS including both Intel and Apple Silicon (M1/M2/M3) Macs.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Intel Mac Installation](#intel-mac-installation)
- [Apple Silicon (M1/M2/M3) Installation](#apple-silicon-m1m2m3-installation)
- [GPU Acceleration](#gpu-acceleration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: macOS 11.0 (Big Sur) or later
- **CPU**: Intel Core i5/i7 or Apple M1/M2/M3
- **RAM**: 8 GB minimum (16+ GB recommended)
- **Storage**: 20 GB free space (50+ GB recommended)
- **Xcode**: Command Line Tools

### Check Your Mac Type

```bash
# Check architecture
uname -m
# x86_64 = Intel
# arm64 = Apple Silicon
```

## Installation Methods

Choose one:
1. **Homebrew (Recommended)** - Easiest method
2. **Manual Installation** - More control
3. **Automated Script** - Quick setup

## Method 1: Homebrew Installation (Recommended)

### Step 1: Install Homebrew

If not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Xcode Command Line Tools

```bash
xcode-select --install
```

### Step 3: Install Python 3.10

```bash
brew install python@3.10
```

### Step 4: Install System Dependencies

```bash
brew install \
    git \
    wget \
    curl \
    openssl@3 \
    readline \
    sqlite3 \
    xz \
    zlib \
    portaudio \
    ffmpeg \
    libxml2 \
    libxmlsec1
```

### Step 5: Clone Repository

```bash
cd ~
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4
```

### Step 6: Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### Step 7: Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
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

## Intel Mac Installation

### Additional Steps for Intel Macs

Intel Macs may benefit from specific optimizations:

```bash
# Install Intel-optimized packages
pip install intel-openmp mkl

# Set environment variables
echo 'export KMP_AFFINITY=granularity=fine,compact,1,0' >> ~/.zshrc
echo 'export OMP_NUM_THREADS=8' >> ~/.zshrc
source ~/.zshrc
```

### Intel Configuration

Edit `~/.sentient-core/config.yaml`:

```yaml
core:
  device: "cpu"
  optimization: "intel"
  threads: 8  # Adjust based on your CPU cores
```

## Apple Silicon (M1/M2/M3) Installation

### Prerequisites for Apple Silicon

```bash
# Install Rosetta 2 (if needed for compatibility)
softwareupdate --install-rosetta

# Use native ARM Python
which python3
# Should show /opt/homebrew/bin/python3
```

### Step 1: Install ARM-Optimized Packages

```bash
# Ensure using ARM Python
arch -arm64 brew install python@3.10

# Clone and setup
cd ~
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4

# Create virtual environment with ARM Python
/opt/homebrew/bin/python3.10 -m venv venv
source venv/bin/activate
```

### Step 2: Install PyTorch for Apple Silicon

```bash
pip install --upgrade pip setuptools wheel

# Install PyTorch with Metal Performance Shaders (MPS) support
pip install torch torchvision torchaudio
```

### Step 3: Install Additional Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### Step 4: Apple Silicon Configuration

```yaml
core:
  device: "mps"  # Use Metal Performance Shaders
  optimization: "apple_silicon"
  metal_acceleration: true
```

### Step 5: Verify Metal/MPS Support

```bash
python3 << EOF
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"MPS Available: {torch.backends.mps.is_available()}")
print(f"MPS Built: {torch.backends.mps.is_built()}")
EOF
```

## GPU Acceleration

### Apple Silicon (Metal)

Apple Silicon Macs use Metal Performance Shaders (MPS) for GPU acceleration:

```bash
# Verify Metal support
sentient-core --check-gpu
```

Configuration:
```yaml
core:
  device: "mps"
  mixed_precision: true
```

### Intel Mac (External GPU)

For Intel Macs with eGPU:

```bash
# Install CUDA (if NVIDIA eGPU)
# Note: NVIDIA support on macOS is limited

# AMD eGPU - use default Metal
```

## Automated Installation

Use our automated setup script:

```bash
cd ~
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4
chmod +x scripts/setup-macos.sh
./scripts/setup-macos.sh
```

The script will:
- Detect Intel vs Apple Silicon
- Install Homebrew if needed
- Install all dependencies
- Set up virtual environment
- Configure optimizations
- Verify installation

## Configuration

### Environment Variables

Add to `~/.zshrc` (or `~/.bash_profile` for bash):

```bash
# Sentient Core
export SENTIENT_HOME=~/.sentient-core
export SENTIENT_CONFIG=$SENTIENT_HOME/config.yaml
export SENTIENT_MODELS=$SENTIENT_HOME/models
export PATH=$PATH:~/sentient-core-v4/venv/bin

# For Intel Macs
export KMP_AFFINITY=granularity=fine,compact,1,0
export OMP_NUM_THREADS=8

# For Apple Silicon
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

Reload:
```bash
source ~/.zshrc
```

### Basic Configuration

Edit configuration:

```bash
nano ~/.sentient-core/config.yaml
```

Example for Apple Silicon:
```yaml
core:
  model: "sentient-v4-base"
  device: "mps"
  max_memory: "8GB"
  optimization: "apple_silicon"

api:
  host: "127.0.0.1"
  port: 8080
  auth_required: true

logging:
  level: "INFO"
  file: "~/.sentient-core/logs/sentient.log"
```

## Running Sentient Core

### Interactive Mode

```bash
# Activate environment
source ~/sentient-core-v4/venv/bin/activate

# Start interactive session
sentient-core interactive
```

### Service Mode

```bash
# Start as service
sentient-core start

# Check status
sentient-core status

# Stop service
sentient-core stop
```

### As LaunchAgent (Background Service)

Create launch agent:

```bash
mkdir -p ~/Library/LaunchAgents
nano ~/Library/LaunchAgents/com.sentient-core.plist
```

Add:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sentient-core</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/sentient-core-v4/venv/bin/sentient-core</string>
        <string>run</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/sentient-core-v4</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/.sentient-core/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/.sentient-core/logs/stderr.log</string>
</dict>
</plist>
```

Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.sentient-core.plist
launchctl start com.sentient-core
```

Check status:
```bash
launchctl list | grep sentient-core
```

## Verification

### System Check

```bash
# Check installation
sentient-core --version
sentient-core --check-system

# Verify Python packages
pip list | grep -i torch
pip list | grep -i sentient

# Check device availability
sentient-core --check-gpu
```

### Run Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

### Benchmark Performance

```bash
sentient-core benchmark --quick
```

## Troubleshooting

### Homebrew Issues

```bash
# Update Homebrew
brew update
brew upgrade

# Fix permissions
sudo chown -R $(whoami) /opt/homebrew  # Apple Silicon
sudo chown -R $(whoami) /usr/local     # Intel
```

### Python Version Conflicts

```bash
# Use specific Python version
brew unlink python && brew link python@3.10

# Verify
python3.10 --version
```

### SSL Certificate Errors

```bash
# Install certificates
/Applications/Python\ 3.10/Install\ Certificates.command

# Or manually
pip install --upgrade certifi
```

### Rosetta Issues (Apple Silicon)

```bash
# Force ARM execution
arch -arm64 /bin/bash
cd ~/sentient-core-v4
source venv/bin/activate

# Reinstall packages
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio
```

### MPS/Metal Not Available

```bash
# Check macOS version (needs 12.3+)
sw_vers

# Update PyTorch
pip install --upgrade torch torchvision torchaudio

# Verify MPS
python3 -c "import torch; print(torch.backends.mps.is_available())"
```

### Port Already in Use

```bash
# Find process
lsof -i :8080

# Kill process
kill -9 <PID>

# Or change port in config
```

### Memory Pressure

```bash
# Check memory usage
sentient-core --memory-stats

# Reduce in config
nano ~/.sentient-core/config.yaml
```

Set:
```yaml
core:
  max_memory: "4GB"
  batch_size: 1
```

### Permission Denied Errors

```bash
# Fix ownership
sudo chown -R $(whoami) ~/sentient-core-v4
sudo chown -R $(whoami) ~/.sentient-core

# Fix permissions
chmod +x scripts/*.sh
chmod 755 ~/sentient-core-v4/venv/bin/*
```

### Library Loading Errors

```bash
# Add to ~/.zshrc
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
source ~/.zshrc

# Reinstall problematic packages
pip install --force-reinstall --no-cache-dir <package-name>
```

## Performance Optimization

### For Apple Silicon

```yaml
core:
  device: "mps"
  optimization: "apple_silicon"
  metal_acceleration: true
  mixed_precision: true
  unified_memory: true  # Use unified memory architecture
```

### For Intel Mac

```yaml
core:
  device: "cpu"
  optimization: "intel"
  threads: 8
  mkl_threads: 8
```

### Disable Unnecessary Features

```yaml
features:
  audio_processing: false
  vision_processing: false
  real_time_mode: false
```

## Updating

```bash
cd ~/sentient-core-v4
source venv/bin/activate

# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Run migrations
sentient-core migrate

# Restart service
sentient-core restart
```

## Uninstallation

```bash
# Stop service
launchctl unload ~/Library/LaunchAgents/com.sentient-core.plist
rm ~/Library/LaunchAgents/com.sentient-core.plist

# Remove files
rm -rf ~/sentient-core-v4
rm -rf ~/.sentient-core

# Remove Homebrew packages (optional)
brew uninstall python@3.10 portaudio ffmpeg
```

## macOS-Specific Features

### Spotlight Integration

Sentient Core can integrate with Spotlight:

```bash
sentient-core integrate --spotlight
```

### Shortcuts Integration

Create automation shortcuts:

```bash
sentient-core integrate --shortcuts
```

### Menu Bar App

Install the menu bar application:

```bash
sentient-core install-menubar
```

## Security and Privacy

### Gatekeeper

If you encounter Gatekeeper warnings:

```bash
xattr -d com.apple.quarantine ~/sentient-core-v4/scripts/*
```

### Permissions

Grant necessary permissions in System Preferences:
- Full Disk Access (if needed)
- Microphone (for audio features)
- Camera (for vision features)

## Next Steps

- [Configuration Guide](../guides/CONFIGURATION.md)
- [User Guide](../guides/USER_GUIDE.md)
- [API Reference](../api/API_REFERENCE.md)
- [Performance Tuning](../guides/PERFORMANCE.md)

## Support

For macOS-specific issues:
- Check [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Report on [GitHub](https://github.com/thotsl4yer69/sentient-core-v4/issues)
- Tag with `macos` and specify Intel/Apple Silicon

#!/bin/bash
#
# Sentient Core v4 - Raspberry Pi 5 + Hailo AI Hat Setup Script
#
# This script installs and configures all dependencies for running
# Sentient Core on Raspberry Pi 5 with Hailo AI accelerator.
#

set -e  # Exit on error

echo "================================================================"
echo "Sentient Core v4 - Pi 5 + Hailo Setup"
echo "================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

function print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

function print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    print_warning "This script is designed for Raspberry Pi 5"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    git cmake build-essential pkg-config \
    python3-dev python3-pip python3-venv \
    libhdf5-dev libatlas-base-dev gfortran libopenblas-dev \
    python3-opencv libopencv-dev \
    portaudio19-dev libsndfile1 alsa-utils \
    i2c-tools python3-smbus \
    ffmpeg v4l-utils \
    avahi-daemon \
    redis-server \
    sqlite3

# Hailo AI Hat setup
print_status "Setting up Hailo AI Hat..."
if [ -f /usr/lib/libhailort.so ]; then
    print_status "Hailo runtime already installed"
else
    print_warning "Hailo runtime not found"
    echo "Please install HailoRT manually from: https://hailo.ai/developer-zone/"
    echo "After installation, re-run this script"
fi

# Google Coral TPU setup (optional)
print_status "Setting up Google Coral TPU (optional)..."
if ! dpkg -l | grep -q "libedgetpu1-std"; then
    echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
        sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
    sudo apt update
    sudo apt install -y libedgetpu1-std python3-pycoral
    print_status "Coral TPU runtime installed"
else
    print_status "Coral TPU runtime already installed"
fi

# Create virtual environment
VENV_DIR="$HOME/sentient_core_env"
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip

# Core dependencies
pip install \
    numpy scipy matplotlib \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    transformers accelerate \
    opencv-python pillow scikit-image \
    librosa soundfile sounddevice pyaudio pydub \
    aiohttp websockets asyncio \
    fastapi uvicorn \
    pyyaml python-dotenv \
    redis hiredis \
    psutil colorlog rich tqdm \
    pytest pytest-asyncio

# Hailo Python bindings
if command -v hailortcli &> /dev/null; then
    pip install hailort || print_warning "Hailo Python package not available"
fi

# Coral Python bindings
pip install pycoral tflite-runtime || print_warning "Coral packages not available via pip"

# llama.cpp for local LLM
print_status "Installing llama-cpp-python..."
pip install llama-cpp-python

# RF processing (optional)
pip install pyrtlsdr || print_warning "RTL-SDR support optional"

# GPIO and hardware interfaces
pip install RPi.GPIO gpiozero smbus2 spidev pyserial

# System configuration
print_status "Configuring system..."

# Increase swap
SWAP_SIZE=2048
print_status "Increasing swap to ${SWAP_SIZE}MB..."
sudo dphys-swapfile swapoff
sudo sed -i "s/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=${SWAP_SIZE}/" /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Enable interfaces
print_status "Enabling I2C, SPI, Serial..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial_hw 0

# Set CPU governor to performance
print_status "Setting CPU to performance mode..."
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo 'GOVERNOR="performance"' | sudo tee -a /etc/default/cpufrequtils 2>/dev/null || true

# Enable Redis
print_status "Enabling Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Clone Sentient Core (if not already present)
if [ ! -d "$HOME/sentient-core-v4" ]; then
    print_status "Cloning Sentient Core repository..."
    cd "$HOME"
    git clone https://github.com/thotsl4yer69/sentient-core-v4.git
    cd sentient-core-v4
else
    print_status "Sentient Core repository already exists"
    cd "$HOME/sentient-core-v4"
fi

# Install Sentient Core
print_status "Installing Sentient Core..."
pip install -e .

# Create directories
print_status "Creating directories..."
mkdir -p "$HOME/.sentient_core/models"
mkdir -p "$HOME/.sentient_core/config"
mkdir -p "$HOME/.sentient_core/logs"
mkdir -p "$HOME/.sentient_core/data/rf_spectrograms"

# Install systemd service
print_status "Installing systemd service..."
sudo tee /etc/systemd/system/sentient-core.service > /dev/null <<EOF
[Unit]
Description=Sentient Core v4 - Distributed AI System
After=network.target redis-server.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$HOME/sentient-core-v4
Environment="PATH=$VENV_DIR/bin:\$PATH"
ExecStart=$VENV_DIR/bin/python -m sentient_core.cli start --config $HOME/.sentient_core/config/pi5_hailo.yaml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable sentient-core.service

print_status "Systemd service installed"

echo ""
echo "================================================================"
echo "Setup Complete!"
echo "================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Download Qwen model:"
echo "   cd $HOME/.sentient_core/models"
echo "   wget https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
echo ""
echo "2. Deploy AI models for Hailo/Coral:"
echo "   cp your_model.hef $HOME/.sentient_core/models/"
echo "   cp your_model_edgetpu.tflite $HOME/.sentient_core/models/"
echo ""
echo "3. Configure Sentient Core:"
echo "   nano $HOME/.sentient_core/config/pi5_hailo.yaml"
echo ""
echo "4. Start service:"
echo "   sudo systemctl start sentient-core"
echo "   sudo systemctl status sentient-core"
echo ""
echo "5. View logs:"
echo "   journalctl -u sentient-core -f"
echo ""
echo "Virtual environment: $VENV_DIR"
echo "Activate with: source $VENV_DIR/bin/activate"
echo ""

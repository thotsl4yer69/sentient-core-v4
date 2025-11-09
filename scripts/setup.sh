#!/bin/bash
# Sentient Core v4 - Automated Setup Script for Linux/macOS
# This script automates the installation process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════╗"
    echo "║     Sentient Core v4 Setup Script        ║"
    echo "║     Automated Installation               ║"
    echo "╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
            VER=$VERSION_ID
        fi
        log_info "Detected Linux: $OS $VER"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        VER=$(sw_vers -productVersion)
        log_info "Detected macOS: $VER"

        # Detect architecture
        ARCH=$(uname -m)
        if [ "$ARCH" = "arm64" ]; then
            log_info "Apple Silicon (M1/M2/M3) detected"
        else
            log_info "Intel Mac detected"
        fi
    else
        log_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check for Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION found"
    else
        log_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi

    # Check for git
    if command -v git &> /dev/null; then
        log_success "Git found"
    else
        log_error "Git not found. Please install git"
        exit 1
    fi

    # Check for pip
    if command -v pip3 &> /dev/null; then
        log_success "pip found"
    else
        log_warning "pip not found, will attempt to install"
    fi
}

# Install system dependencies
install_dependencies() {
    log_info "Installing system dependencies..."

    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        log_info "Installing dependencies for Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y \
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
            portaudio19-dev \
            ffmpeg
    elif [[ "$OS" == "fedora" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "centos" ]]; then
        log_info "Installing dependencies for Fedora/RHEL/CentOS..."
        sudo dnf install -y \
            python3.10 \
            python3-devel \
            gcc \
            gcc-c++ \
            git \
            curl \
            wget \
            openssl-devel \
            portaudio-devel \
            ffmpeg
    elif [[ "$OS" == "arch" ]] || [[ "$OS" == "manjaro" ]]; then
        log_info "Installing dependencies for Arch Linux..."
        sudo pacman -S --needed --noconfirm \
            python \
            python-pip \
            base-devel \
            git \
            curl \
            wget \
            portaudio \
            ffmpeg
    elif [[ "$OS" == "macos" ]]; then
        log_info "Installing dependencies for macOS..."

        # Check for Homebrew
        if ! command -v brew &> /dev/null; then
            log_warning "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi

        brew install python@3.10 git curl wget portaudio ffmpeg
    fi

    log_success "System dependencies installed"
}

# Setup virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."

    # Create virtual environment
    python3 -m venv venv

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    log_success "Virtual environment created and activated"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."

    # Activate virtual environment
    source venv/bin/activate

    # Install requirements
    pip install -r requirements.txt

    # Install in editable mode
    pip install -e .

    log_success "Python dependencies installed"
}

# Initialize configuration
init_config() {
    log_info "Initializing configuration..."

    # Create config directory
    mkdir -p ~/.sentient-core
    mkdir -p ~/.sentient-core/logs
    mkdir -p ~/.sentient-core/models

    # Copy default config if not exists
    if [ ! -f ~/.sentient-core/config.yaml ]; then
        cp config/default.yaml ~/.sentient-core/config.yaml
        log_success "Default configuration created at ~/.sentient-core/config.yaml"
    else
        log_warning "Configuration already exists, skipping"
    fi
}

# Setup environment variables
setup_env() {
    log_info "Setting up environment variables..."

    # Determine shell config file
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.profile"
    fi

    # Add environment variables if not already present
    if ! grep -q "SENTIENT_HOME" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Sentient Core v4" >> "$SHELL_RC"
        echo "export SENTIENT_HOME=~/.sentient-core" >> "$SHELL_RC"
        echo "export SENTIENT_CONFIG=\$SENTIENT_HOME/config.yaml" >> "$SHELL_RC"
        echo "export SENTIENT_MODELS=\$SENTIENT_HOME/models" >> "$SHELL_RC"
        log_success "Environment variables added to $SHELL_RC"
    else
        log_warning "Environment variables already set, skipping"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    source venv/bin/activate

    # Check if sentient-core command exists
    if command -v sentient-core &> /dev/null; then
        VERSION=$(sentient-core --version 2>&1 || echo "unknown")
        log_success "Sentient Core installed: $VERSION"
    else
        log_warning "sentient-core command not found (this is okay for development)"
    fi

    # Check Python imports
    python3 -c "import torch; print(f'PyTorch: {torch.__version__}')" 2>/dev/null && log_success "PyTorch import successful" || log_warning "PyTorch import failed"
    python3 -c "import transformers; print(f'Transformers: {transformers.__version__}')" 2>/dev/null && log_success "Transformers import successful" || log_warning "Transformers import failed"
}

# GPU setup (optional)
setup_gpu() {
    log_info "Checking for GPU support..."

    if command -v nvidia-smi &> /dev/null; then
        log_success "NVIDIA GPU detected"
        nvidia-smi --query-gpu=name --format=csv,noheader

        read -p "Would you like to install GPU-accelerated packages? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            source venv/bin/activate
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
            log_success "GPU packages installed"
        fi
    else
        log_info "No NVIDIA GPU detected, using CPU packages"
    fi
}

# Main installation flow
main() {
    print_banner

    log_info "Starting Sentient Core v4 installation..."
    echo

    # Run installation steps
    detect_os
    check_prerequisites

    read -p "Install system dependencies? (requires sudo) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
    fi

    setup_venv
    install_python_deps
    init_config
    setup_env
    setup_gpu
    verify_installation

    echo
    log_success "Installation complete!"
    echo
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
    echo "2. Activate virtual environment: source venv/bin/activate"
    echo "3. Configure: nano ~/.sentient-core/config.yaml"
    echo "4. Run: sentient-core --version"
    echo
    echo -e "${BLUE}Documentation:${NC}"
    echo "- User Guide: docs/guides/USER_GUIDE.md"
    echo "- API Reference: docs/api/API_REFERENCE.md"
    echo
}

# Run main function
main "$@"

# Sentient Core v4 - Automated Setup Script for Windows
# PowerShell script for Windows installation

# Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Banner
function Show-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║     Sentient Core v4 Setup Script        ║" -ForegroundColor Blue
    Write-Host "║     Windows Installation                 ║" -ForegroundColor Blue
    Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

# Check if running as Administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    }
    catch {
        Write-Error-Custom "Python not found. Please install Python 3.9+ from python.org"
        Write-Host "Download: https://www.python.org/downloads/"
        exit 1
    }

    # Check Git
    try {
        $gitVersion = git --version 2>&1
        Write-Success "Git found: $gitVersion"
    }
    catch {
        Write-Error-Custom "Git not found. Please install Git"
        Write-Host "Download: https://git-scm.com/download/win"
        exit 1
    }

    # Check pip
    try {
        $pipVersion = pip --version 2>&1
        Write-Success "pip found: $pipVersion"
    }
    catch {
        Write-Warning "pip not found, attempting to install..."
        python -m ensurepip --upgrade
    }
}

# Setup virtual environment
function New-VirtualEnvironment {
    Write-Info "Creating Python virtual environment..."

    # Create venv
    python -m venv venv

    # Activate venv
    & .\venv\Scripts\Activate.ps1

    # Upgrade pip
    python -m pip install --upgrade pip setuptools wheel

    Write-Success "Virtual environment created"
}

# Install Python dependencies
function Install-PythonDependencies {
    Write-Info "Installing Python dependencies..."

    # Activate venv
    & .\venv\Scripts\Activate.ps1

    # Install requirements
    pip install -r requirements.txt

    # Install in editable mode
    pip install -e .

    Write-Success "Python dependencies installed"
}

# Initialize configuration
function Initialize-Configuration {
    Write-Info "Initializing configuration..."

    # Create directories
    $configDir = "$env:USERPROFILE\.sentient-core"
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    New-Item -ItemType Directory -Force -Path "$configDir\logs" | Out-Null
    New-Item -ItemType Directory -Force -Path "$configDir\models" | Out-Null

    # Copy default config
    $configFile = "$configDir\config.yaml"
    if (-not (Test-Path $configFile)) {
        Copy-Item "config\default.yaml" $configFile
        Write-Success "Configuration created at $configFile"
    }
    else {
        Write-Warning "Configuration already exists, skipping"
    }
}

# Setup environment variables
function Set-EnvironmentVariables {
    Write-Info "Setting up environment variables..."

    # Set user environment variables
    [System.Environment]::SetEnvironmentVariable('SENTIENT_HOME', "$env:USERPROFILE\.sentient-core", 'User')
    [System.Environment]::SetEnvironmentVariable('SENTIENT_CONFIG', "$env:USERPROFILE\.sentient-core\config.yaml", 'User')
    [System.Environment]::SetEnvironmentVariable('SENTIENT_MODELS', "$env:USERPROFILE\.sentient-core\models", 'User')

    # Add to PATH
    $currentPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
    $venvPath = "$pwd\venv\Scripts"
    if ($currentPath -notlike "*$venvPath*") {
        $newPath = "$venvPath;$currentPath"
        [System.Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')
        Write-Success "Environment variables set"
    }
    else {
        Write-Warning "Path already configured"
    }
}

# Check for GPU
function Test-GPU {
    Write-Info "Checking for NVIDIA GPU..."

    try {
        $nvidiaOutput = nvidia-smi --query-gpu=name --format=csv,noheader 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "NVIDIA GPU detected: $nvidiaOutput"

            $response = Read-Host "Install GPU-accelerated packages? (y/n)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                & .\venv\Scripts\Activate.ps1
                pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
                Write-Success "GPU packages installed"
            }
        }
    }
    catch {
        Write-Info "No NVIDIA GPU detected, using CPU packages"
    }
}

# Verify installation
function Test-Installation {
    Write-Info "Verifying installation..."

    & .\venv\Scripts\Activate.ps1

    # Test imports
    try {
        $torchVersion = python -c "import torch; print(torch.__version__)" 2>&1
        Write-Success "PyTorch imported successfully: $torchVersion"
    }
    catch {
        Write-Warning "PyTorch import failed"
    }

    try {
        $transformersVersion = python -c "import transformers; print(transformers.__version__)" 2>&1
        Write-Success "Transformers imported successfully: $transformersVersion"
    }
    catch {
        Write-Warning "Transformers import failed"
    }
}

# Main installation
function Start-Installation {
    Show-Banner

    Write-Info "Starting Sentient Core v4 installation for Windows..."
    Write-Host ""

    # Check if running as admin
    if (-not (Test-Administrator)) {
        Write-Warning "Not running as Administrator. Some operations may fail."
        $response = Read-Host "Continue anyway? (y/n)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            exit
        }
    }

    # Run installation steps
    Test-Prerequisites
    New-VirtualEnvironment
    Install-PythonDependencies
    Initialize-Configuration
    Set-EnvironmentVariables
    Test-GPU
    Test-Installation

    Write-Host ""
    Write-Success "Installation complete!"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Green
    Write-Host "1. Restart PowerShell to load environment variables"
    Write-Host "2. Activate virtual environment: .\venv\Scripts\Activate.ps1"
    Write-Host "3. Configure: notepad $env:USERPROFILE\.sentient-core\config.yaml"
    Write-Host "4. Run: sentient-core --version"
    Write-Host ""
    Write-Host "Documentation:" -ForegroundColor Blue
    Write-Host "- Installation Guide: docs\installation\INSTALL_WINDOWS.md"
    Write-Host "- User Guide: docs\guides\USER_GUIDE.md"
    Write-Host ""
}

# Run installation
Start-Installation

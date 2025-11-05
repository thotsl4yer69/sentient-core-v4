# Sentient Core v4 - Windows Installation Guide

Complete installation guide for Windows 10 and Windows 11, including native Windows, WSL2, and containerized installations.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Native Windows Installation](#native-windows-installation)
- [WSL2 Installation (Recommended)](#wsl2-installation-recommended)
- [GPU Support (NVIDIA)](#gpu-support-nvidia)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Windows 10 (version 2004+) or Windows 11
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8 GB minimum (16+ GB recommended)
- **Storage**: 20 GB free space (50+ GB recommended)
- **Python**: 3.9, 3.10, or 3.11
- **Administrator Access**: Required for installation

### Check Windows Version

```powershell
# Open PowerShell and run:
winver
```

## Installation Methods

Three methods available:

1. **WSL2 (Recommended)** - Best performance and compatibility
2. **Native Windows** - Direct Windows installation
3. **Docker** - Containerized deployment

## WSL2 Installation (Recommended)

WSL2 provides the best Linux compatibility and performance on Windows.

### Step 1: Enable WSL2

Open PowerShell as Administrator:

```powershell
# Enable WSL
wsl --install

# Or if WSL is already installed
wsl --set-default-version 2
```

Restart your computer if prompted.

### Step 2: Install Ubuntu

```powershell
# Install Ubuntu 22.04
wsl --install -d Ubuntu-22.04

# Launch Ubuntu
wsl -d Ubuntu-22.04
```

### Step 3: Update Ubuntu

Inside WSL2 Ubuntu:

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 4: Follow Linux Installation

Once in WSL2, follow the [Linux Installation Guide](INSTALL_LINUX.md) for Ubuntu.

Quick summary:

```bash
# Install dependencies
sudo apt install -y python3.10 python3.10-dev python3-pip python3-venv \
    build-essential git curl wget

# Clone repository
cd ~
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4

# Setup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .

# Initialize
mkdir -p ~/.sentient-core
cp config/default.yaml ~/.sentient-core/config.yaml

# Verify
sentient-core --version
```

### Step 5: Access from Windows

From Windows, you can access WSL2:

```powershell
# Run sentient-core from Windows
wsl -d Ubuntu-22.04 -e bash -c "cd ~/sentient-core-v4 && source venv/bin/activate && sentient-core --version"

# Access WSL filesystem
explorer.exe \\wsl$\Ubuntu-22.04\home\yourusername\sentient-core-v4
```

## Native Windows Installation

### Step 1: Install Python

Download and install Python 3.10 from [python.org](https://www.python.org/downloads/):

1. Download Python 3.10.x installer
2. **Important**: Check "Add Python to PATH"
3. Click "Install Now"
4. Verify installation:

```powershell
python --version
pip --version
```

### Step 2: Install Git

Download and install from [git-scm.com](https://git-scm.com/download/win):

1. Download Git installer
2. Use default options
3. Verify:

```powershell
git --version
```

### Step 3: Install Build Tools

Download and install:
- [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Select "Desktop development with C++"

Or install Visual Studio Community with C++ support.

### Step 4: Install Additional Dependencies

Install using winget or manually:

```powershell
# Using winget (Windows 11 or Windows 10 with App Installer)
winget install FFmpeg
winget install Git.Git

# Or download manually:
# - FFmpeg: https://ffmpeg.org/download.html#build-windows
# - Add to PATH
```

### Step 5: Clone Repository

```powershell
# Open PowerShell
cd $HOME
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4
```

### Step 6: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Note**: If you get execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 7: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Install Sentient Core
pip install -e .
```

### Step 8: Initialize Configuration

```powershell
# Create config directory
New-Item -ItemType Directory -Force -Path "$HOME\.sentient-core"

# Copy default config
Copy-Item config\default.yaml "$HOME\.sentient-core\config.yaml"
```

### Step 9: Verify Installation

```powershell
sentient-core --version
sentient-core --check-system
```

## GPU Support (NVIDIA)

For NVIDIA GPU acceleration on Windows:

### Step 1: Install NVIDIA Drivers

1. Download latest drivers from [NVIDIA](https://www.nvidia.com/download/index.aspx)
2. Install and restart

### Step 2: Install CUDA Toolkit

Download and install [CUDA Toolkit 12.1](https://developer.nvidia.com/cuda-downloads):

```powershell
# Verify installation
nvcc --version
nvidia-smi
```

### Step 3: Install cuDNN

1. Download [cuDNN](https://developer.nvidia.com/cudnn) (requires NVIDIA account)
2. Extract to CUDA installation directory
3. Add to PATH

### Step 4: Install PyTorch with CUDA

#### Native Windows:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install PyTorch with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### WSL2:

```bash
# In WSL2
source venv/bin/activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 5: Verify GPU Support

```powershell
# Native Windows
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

# WSL2
wsl -e python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

## Automated Installation

### PowerShell Script (Native Windows)

```powershell
# Download and run setup script
cd $HOME
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4
.\scripts\setup-windows.ps1
```

### WSL2 Script

```bash
# In WSL2
cd ~
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## Configuration

### Environment Variables (Native Windows)

Add to System Environment Variables:

```powershell
# Using PowerShell (Permanent)
[System.Environment]::SetEnvironmentVariable('SENTIENT_HOME', "$HOME\.sentient-core", 'User')
[System.Environment]::SetEnvironmentVariable('SENTIENT_CONFIG', "$HOME\.sentient-core\config.yaml", 'User')

# Or add to PATH
$newPath = "$HOME\sentient-core-v4\venv\Scripts;" + [System.Environment]::GetEnvironmentVariable('PATH', 'User')
[System.Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')
```

### Basic Configuration

Edit configuration file:

```powershell
notepad "$HOME\.sentient-core\config.yaml"
```

Example configuration:

```yaml
core:
  model: "sentient-v4-base"
  device: "cuda"  # or "cpu"
  max_memory: "8GB"

api:
  host: "127.0.0.1"
  port: 8080
  auth_required: true

logging:
  level: "INFO"
  file: "~/.sentient-core/logs/sentient.log"
```

## Running Sentient Core

### Native Windows

```powershell
# Activate virtual environment
cd $HOME\sentient-core-v4
.\venv\Scripts\Activate.ps1

# Start service
sentient-core start

# Or run interactively
sentient-core run
```

### WSL2

```bash
# From Windows, run in WSL2
wsl -d Ubuntu-22.04 -e bash -c "cd ~/sentient-core-v4 && source venv/bin/activate && sentient-core start"
```

### As Windows Service

Create a Windows Service using NSSM (Non-Sucking Service Manager):

1. Download [NSSM](https://nssm.cc/download)
2. Extract to a folder
3. Open PowerShell as Administrator:

```powershell
# Install service
.\nssm.exe install SentientCore "$HOME\sentient-core-v4\venv\Scripts\python.exe" "$HOME\sentient-core-v4\venv\Scripts\sentient-core" "run"

# Set working directory
.\nssm.exe set SentientCore AppDirectory "$HOME\sentient-core-v4"

# Start service
Start-Service SentientCore

# Check status
Get-Service SentientCore
```

## Windows-Specific Features

### Windows Terminal Integration

Add profile to Windows Terminal:

```json
{
    "name": "Sentient Core",
    "commandline": "powershell.exe -NoExit -Command \"cd $HOME\\sentient-core-v4; .\\venv\\Scripts\\Activate.ps1\"",
    "icon": "%USERPROFILE%\\sentient-core-v4\\icon.png"
}
```

### Task Scheduler Integration

Create scheduled task:

```powershell
# Create task to run on startup
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File $HOME\sentient-core-v4\scripts\start.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "SentientCore" -Description "Start Sentient Core on boot"
```

## Verification

### System Check

```powershell
# Check installation
sentient-core --version
sentient-core --check-system
sentient-core --check-gpu

# List installed packages
pip list | Select-String "sentient\|torch"
```

### Run Tests

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run tests
pytest tests\ -v
```

## Troubleshooting

### Python Not Found

```powershell
# Add Python to PATH manually
$env:Path += ";C:\Users\YourUsername\AppData\Local\Programs\Python\Python310;C:\Users\YourUsername\AppData\Local\Programs\Python\Python310\Scripts"

# Make permanent
[System.Environment]::SetEnvironmentVariable('PATH', $env:Path, 'User')
```

### Virtual Environment Activation Issues

```powershell
# Change execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use alternative activation
.\venv\Scripts\activate.bat  # Use CMD instead
```

### Long Path Issues

Windows has 260 character path limit. Enable long paths:

```powershell
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### SSL Certificate Errors

```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade certifi
```

### CUDA Not Found

```powershell
# Check CUDA installation
nvcc --version

# Add CUDA to PATH
$env:Path += ";C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin"
[System.Environment]::SetEnvironmentVariable('PATH', $env:Path, 'User')

# Set CUDA_PATH
[System.Environment]::SetEnvironmentVariable('CUDA_PATH', 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1', 'User')
```

### WSL2 Issues

```powershell
# Update WSL2
wsl --update

# Restart WSL2
wsl --shutdown
wsl -d Ubuntu-22.04

# Check WSL version
wsl -l -v
```

### Port Already in Use

```powershell
# Find process using port
netstat -ano | findstr :8080

# Kill process
taskkill /PID <PID> /F

# Or change port in config
```

### Memory Issues

```powershell
# Check memory usage
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10

# Reduce memory in config
notepad "$HOME\.sentient-core\config.yaml"
```

Set:
```yaml
core:
  max_memory: "4GB"
  batch_size: 1
```

### Dependencies Compilation Errors

```powershell
# Install Visual Studio Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or use pre-built wheels
pip install --only-binary :all: package-name
```

### Antivirus Interference

Add exceptions for:
- `%USERPROFILE%\sentient-core-v4`
- `%USERPROFILE%\.sentient-core`
- Python executable

## Performance Optimization

### Native Windows

```yaml
core:
  device: "cuda"  # or "cpu"
  optimization: "windows"
  threads: 8
```

### WSL2

```yaml
core:
  device: "cuda"
  optimization: "wsl2"
  wsl_integration: true
```

### Disable Windows Defender Realtime Scanning (Optional)

For better performance during development:

```powershell
# Temporary disable (requires Admin)
Set-MpPreference -DisableRealtimeMonitoring $true

# Add exclusion
Add-MpPreference -ExclusionPath "$HOME\sentient-core-v4"
```

## Updating

### Native Windows

```powershell
cd $HOME\sentient-core-v4
.\venv\Scripts\Activate.ps1

git pull origin main
pip install --upgrade -r requirements.txt
sentient-core migrate
```

### WSL2

```bash
cd ~/sentient-core-v4
source venv/bin/activate
git pull origin main
pip install --upgrade -r requirements.txt
sentient-core migrate
```

## Uninstallation

### Native Windows

```powershell
# Stop service
Stop-Service SentientCore -ErrorAction SilentlyContinue
sc.exe delete SentientCore

# Remove files
Remove-Item -Recurse -Force "$HOME\sentient-core-v4"
Remove-Item -Recurse -Force "$HOME\.sentient-core"

# Remove from PATH (manual via System Properties)
```

### WSL2

```bash
# Remove from WSL2
rm -rf ~/sentient-core-v4
rm -rf ~/.sentient-core
```

## Best Practices

### For Native Windows
- Use PowerShell 7+ for better compatibility
- Keep Windows and drivers updated
- Use SSD for better performance
- Monitor resource usage

### For WSL2
- Allocate sufficient resources to WSL2
- Use WSL2 for development, Windows for GUI
- Keep WSL2 kernel updated
- Use VS Code with Remote-WSL extension

## Next Steps

- [Configuration Guide](../guides/CONFIGURATION.md)
- [User Guide](../guides/USER_GUIDE.md)
- [API Reference](../api/API_REFERENCE.md)
- [Docker Installation](INSTALL_DOCKER.md) (Alternative)

## Support

For Windows-specific issues:
- Check [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Report on [GitHub](https://github.com/thotsl4yer69/sentient-core-v4/issues)
- Tag with `windows` and specify Native/WSL2

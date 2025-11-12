#!/bin/bash
# RTL-SDR Setup Script for Raspberry Pi
#
# This script configures a Raspberry Pi to properly use RTL-SDR dongles
# Addresses common issues with USB permissions and kernel driver conflicts

set -e

echo "========================================="
echo "RTL-SDR Setup for Raspberry Pi"
echo "========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /sys/firmware/devicetree/base/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Require sudo for system changes
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo:"
    echo "  sudo $0"
    exit 1
fi

echo "Step 1: Installing RTL-SDR software..."
echo "---------------------------------------"

# Update package lists
apt-get update

# Install RTL-SDR tools and libraries
apt-get install -y rtl-sdr libusb-1.0-0-dev

# Install Python RTL-SDR library
pip3 install pyrtlsdr

echo "✓ RTL-SDR software installed"
echo ""

echo "Step 2: Blacklisting DVB kernel drivers..."
echo "-------------------------------------------"

# Create blacklist file to prevent DVB drivers from loading
cat > /etc/modprobe.d/blacklist-rtl-sdr.conf << 'EOF'
# Blacklist DVB drivers that conflict with RTL-SDR
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
EOF

echo "✓ DVB drivers blacklisted"
echo ""

echo "Step 3: Setting up udev rules..."
echo "---------------------------------"

# Create udev rule for RTL-SDR device permissions
cat > /etc/udev/rules.d/20-rtlsdr.rules << 'EOF'
# RTL-SDR device permissions
# Realtek RTL2838 (generic RTL-SDR)
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE="0666", GROUP="plugdev"

# Additional RTL-SDR variant IDs
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2832", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2837", MODE="0666", GROUP="plugdev"
EOF

# Reload udev rules
udevadm control --reload-rules
udevadm trigger

echo "✓ udev rules configured"
echo ""

echo "Step 4: Adding user to plugdev group..."
echo "----------------------------------------"

# Get the actual user (not root when using sudo)
ACTUAL_USER=${SUDO_USER:-$USER}

# Add user to plugdev group
usermod -a -G plugdev $ACTUAL_USER

echo "✓ User $ACTUAL_USER added to plugdev group"
echo ""

echo "Step 5: Checking for RTL-SDR device..."
echo "---------------------------------------"

# Check if RTL-SDR device is connected
if lsusb | grep -q "Realtek.*RTL"; then
    echo "✓ RTL-SDR device detected:"
    lsusb | grep "Realtek.*RTL"
else
    echo "⚠️  No RTL-SDR device detected"
    echo "   Please plug in your RTL-SDR dongle and run: lsusb"
fi

echo ""
echo "Step 6: Unloading conflicting kernel modules..."
echo "------------------------------------------------"

# Unload DVB modules if currently loaded
MODULES_TO_REMOVE="dvb_usb_rtl28xxu rtl2832 rtl2830"
for module in $MODULES_TO_REMOVE; do
    if lsmod | grep -q $module; then
        echo "Removing $module..."
        rmmod $module 2>/dev/null || true
    fi
done

echo "✓ Conflicting modules removed"
echo ""

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "IMPORTANT: Please reboot your Raspberry Pi for all changes to take effect:"
echo "  sudo reboot"
echo ""
echo "After reboot, test RTL-SDR with:"
echo "  rtl_test -t"
echo ""
echo "To test with Sentient Core:"
echo "  python3 -c 'from sentient_core.sensors.rf_monitor import RFMonitor; m = RFMonitor(); m.initialize()'"
echo ""
echo "Troubleshooting:"
echo "  - Check USB connection: lsusb | grep Realtek"
echo "  - Check modules: lsmod | grep dvb"
echo "  - Check groups: groups (should include 'plugdev')"
echo "  - Check device permissions: ls -l /dev/bus/usb/*/*"
echo ""

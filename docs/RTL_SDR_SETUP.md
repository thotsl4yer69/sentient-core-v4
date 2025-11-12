# RTL-SDR Setup Guide for Raspberry Pi

## Overview

Setting up RTL-SDR on Raspberry Pi requires addressing several common issues:
1. USB permissions
2. Kernel driver conflicts (DVB drivers)
3. USB power/stability
4. Library installation

## Quick Setup

### Automated Setup (Recommended)

Run the automated setup script:

```bash
sudo bash scripts/setup_rtlsdr_pi.sh
sudo reboot
```

### Manual Setup

If you prefer to set up manually, follow these steps:

#### 1. Install RTL-SDR Software

```bash
sudo apt-get update
sudo apt-get install -y rtl-sdr libusb-1.0-0-dev
pip3 install pyrtlsdr
```

#### 2. Blacklist DVB Kernel Drivers

The DVB drivers will claim the RTL-SDR device and prevent access. Blacklist them:

```bash
sudo tee /etc/modprobe.d/blacklist-rtl-sdr.conf << EOF
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
EOF
```

#### 3. Set Up USB Permissions

Create udev rules for proper device permissions:

```bash
sudo tee /etc/udev/rules.d/20-rtlsdr.rules << EOF
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE="0666", GROUP="plugdev"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 4. Add User to plugdev Group

```bash
sudo usermod -a -G plugdev $USER
```

**Important:** Log out and log back in for group changes to take effect.

#### 5. Reboot

```bash
sudo reboot
```

## Testing

After reboot, test your RTL-SDR:

```bash
# Test with RTL-SDR tools
rtl_test -t

# Test frequency correction
rtl_test -p

# Test with Sentient Core
python3 << EOF
from sentient_core.sensors.rf_monitor import RFMonitor

monitor = RFMonitor()
if monitor.initialize():
    print("✓ RTL-SDR initialized successfully!")
else:
    print("✗ RTL-SDR initialization failed")
EOF
```

## Common Issues and Solutions

### Issue: "Permission denied" Error

**Symptom:** `OSError: Permission denied` when accessing RTL-SDR

**Solution:**
```bash
# Check if you're in plugdev group
groups

# If not, add yourself
sudo usermod -a -G plugdev $USER

# Log out and log back in
```

### Issue: "Resource busy" or "LIBUSB_ERROR_BUSY"

**Symptom:** Device is busy, can't access

**Solution:** DVB kernel driver is loaded

```bash
# Check if DVB modules are loaded
lsmod | grep dvb

# If loaded, blacklist them
sudo tee /etc/modprobe.d/blacklist-rtl-sdr.conf << EOF
blacklist dvb_usb_rtl28xxu
EOF

# Reboot
sudo reboot
```

### Issue: "No devices found"

**Symptom:** RTL-SDR not detected

**Solutions:**

1. **Check USB connection:**
   ```bash
   lsusb | grep Realtek
   ```
   Should show: `Bus XXX Device XXX: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T`

2. **Try different USB port:**
   - Use USB 2.0 port (not USB 3.0)
   - Use powered USB hub if Pi power is insufficient

3. **Check dmesg for errors:**
   ```bash
   dmesg | tail -20
   ```

### Issue: Unstable USB Connection

**Symptom:** Device disconnects or becomes unresponsive

**Solutions:**

1. **Increase USB power:**
   Add to `/boot/config.txt`:
   ```
   max_usb_current=1
   ```

2. **Use powered USB hub:**
   RTL-SDR can draw significant current

3. **Lower sample rate:**
   In your config, use lower sample rate (e.g., 1 MHz instead of 2.4 MHz)

4. **Reduce RF gain:**
   Lower gain settings are more stable

### Issue: Poor Performance on Raspberry Pi

**Optimization tips:**

1. **Lower sample rate:**
   ```python
   config.rf_sample_rate = 1.0e6  # 1 MHz
   ```

2. **Use manual gain:**
   ```python
   config.rf_gain = 30  # Instead of 'auto'
   ```

3. **Increase process priority:**
   ```bash
   sudo nice -n -20 python3 your_script.py
   ```

4. **Disable WiFi/Bluetooth if not needed:**
   ```bash
   sudo rfkill block wifi
   sudo rfkill block bluetooth
   ```

## Frequency Correction (PPM)

RTL-SDR dongles often have frequency drift. To calibrate:

1. **Find your PPM offset:**
   Use `kalibrate-rtl` or tune to a known frequency (e.g., FM radio)

2. **Set in config:**
   ```yaml
   rf_freq_correction: 0  # Your PPM offset (e.g., -15, +23)
   ```

## Configuration Example

Example config for Raspberry Pi:

```yaml
sensors:
  rf:
    enabled: true
    rf_sample_rate: 1.0e6      # 1 MHz (stable on Pi)
    rf_center_freq: 2.4e9       # 2.4 GHz
    rf_gain: 30                 # Manual gain
    rf_freq_correction: 0       # Your PPM offset
```

## Hardware Recommendations

**Recommended RTL-SDR Dongles:**
- RTL-SDR Blog V3 (has bias-tee, better TCXO)
- NooElec NESDR Smart
- Generic RTL2832U (basic but works)

**Raspberry Pi Models:**
- **Best:** Pi 4 (4GB+ RAM)
- **Good:** Pi 3B+
- **Okay:** Pi 3B, Pi Zero 2 W
- **Not recommended:** Pi Zero W (too slow for real-time)

## Integration with Sentient Core

Once RTL-SDR is working, integrate with Sentient Core:

```python
from sentient_core.sensors.rf_monitor import RFMonitor
from sentient_core.sensors.rf_signal_analysis import RFSignalAnalyzer, DroneSignatureDetector

# Initialize RF monitor
monitor = RFMonitor(config)
monitor.initialize()
monitor.start()

# Set up signal analysis
analyzer = RFSignalAnalyzer(sample_rate=monitor.sample_rate)
drone_detector = DroneSignatureDetector(analyzer)

# Monitor for drones
while True:
    detections = monitor.get_detections()
    if detections:
        drones = drone_detector.analyze_for_drones(samples, monitor.center_frequency)
        for drone in drones:
            print(f"Drone detected: {drone['model']} @ {drone['frequency']/1e9:.3f} GHz")

    time.sleep(1)
```

## References

- [RTL-SDR Quick Start Guide](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/)
- [Raspberry Pi RTL-SDR Guide](https://ranous.files.wordpress.com/2018/02/rtl-sdr4linux_quickstartguidev10-18.pdf)
- [pyrtlsdr Documentation](https://pyrtlsdr.readthedocs.io/)

## Support

If you encounter issues:

1. Check the logs: `journalctl -f | grep sentient`
2. Enable debug logging in config
3. Run diagnostic: `rtl_test -t`
4. Check GitHub issues: https://github.com/thotsl4yer69/sentient-core-v4/issues

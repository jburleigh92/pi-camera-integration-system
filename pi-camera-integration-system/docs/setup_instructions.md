# Setup Instructions

Complete guide to deploying the Pi Camera Integration System on a Raspberry Pi 4.

---

## Prerequisites

### Hardware
- ✓ Raspberry Pi 4 (2GB RAM minimum, 4GB recommended)
- ✓ MicroSD card (16GB minimum, 32GB recommended)
- ✓ USB Webcam (V4L2-compatible)
- ✓ Power supply (Official Raspberry Pi power supply recommended)
- ✓ USB keyboard and mouse (for initial setup)
- ✓ Monitor with HDMI cable
- ✓ Ethernet cable or WiFi connection

### Software
- ✓ Raspberry Pi OS (Bullseye Legacy recommended)
- ✓ SSH access (optional, for remote management)

---

## Step 1: Prepare Raspberry Pi

### Install Operating System

1. **Download Raspberry Pi Imager**
   - Visit: https://www.raspberrypi.com/software/
   - Download for your operating system

2. **Flash SD Card**
   - Insert microSD card into computer
   - Open Raspberry Pi Imager
   - Choose OS: **Raspberry Pi OS (Legacy)**
   - Choose Storage: Your microSD card
   - Click **Write**
   - Wait for completion

3. **Configure Initial Settings** (Optional)
   - Click gear icon in Imager for advanced options
   - Set hostname: `picamera`
   - Enable SSH
   - Set username/password
   - Configure WiFi (if needed)

4. **Boot Raspberry Pi**
   - Insert microSD card into Pi
   - Connect monitor, keyboard, mouse
   - Connect power
   - Wait for first boot (may take 2-3 minutes)

---

## Step 2: Initial System Configuration

### Update System

```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Reboot
sudo reboot
```

### Configure Raspberry Pi Settings

```bash
# Open configuration tool
sudo raspi-config
```

**Recommended Settings:**
- Interface Options → Camera: Enable (if using Pi Camera, optional)
- Localization Options → Set your timezone
- System Options → Set hostname
- Advanced Options → Expand Filesystem

---

## Step 3: Install Dependencies

### Clone/Download Project

```bash
# Navigate to home directory
cd ~

# Option 1: Clone from Git (if available)
git clone <repository-url> pi-camera-integration-system

# Option 2: Download and extract manually
# (Transfer files via USB, SCP, or download)

# Navigate into project
cd pi-camera-integration-system
```

### Run Installation Script

```bash
# Make script executable (if not already)
chmod +x scripts/install_dependencies.sh

# Run installation
./scripts/install_dependencies.sh
```

This script will:
- Update apt package list
- Install fswebcam
- Install v4l-utils
- Install Python dependencies
- Add user to video group
- Verify installations

### Manual Installation (if script fails)

```bash
# Install system packages
sudo apt install -y fswebcam v4l-utils python3 python3-pip python3-yaml

# Install Python packages
pip3 install -r requirements.txt

# Add user to video group
sudo usermod -a -G video $USER

# Log out and log back in for group changes
```

---

## Step 4: Connect and Test Camera

### Connect Camera

1. **Power off Raspberry Pi**
   ```bash
   sudo shutdown -h now
   ```

2. **Connect USB webcam** to any USB port

3. **Power on Raspberry Pi**

### Verify Camera Detection

```bash
# List video devices
ls -l /dev/video*

# Should show something like:
# crw-rw---- 1 root video 81, 0 Jan 10 14:30 /dev/video0

# Get detailed camera info
v4l2-ctl --device /dev/video0 --all

# List supported formats
v4l2-ctl --device /dev/video0 --list-formats-ext
```

### Test Camera Manually

```bash
# Capture test image
fswebcam -r 1280x720 --no-banner test.jpg

# View image (if GUI available)
display test.jpg

# Or check file size
ls -lh test.jpg

# Clean up
rm test.jpg
```

---

## Step 5: Configure System

### Review Configuration

```bash
cd ~/pi-camera-integration-system

# View current configuration
cat config/default_config.yaml
```

### Customize Settings (Optional)

Edit configuration file:
```bash
nano config/default_config.yaml
```

**Common Customizations:**

```yaml
# Change capture interval
capture:
  interval: 30  # seconds between captures

# Change resolution
camera:
  resolution: "1920x1080"  # Higher resolution

# Change storage duration
files:
  max_capture_age_days: 14  # Keep for 2 weeks

# Adjust logging
logging:
  level: "DEBUG"  # More verbose logging
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

---

## Step 6: Run Initial Test

### Single Capture Test

```bash
# Run one-time capture test
./scripts/run_once.sh
```

**Expected Output:**
```
==========================================
Pi Camera Integration System
Single Capture Test
==========================================

Configuration Summary
==========================================
Camera Device: /dev/video0
Resolution: 1280x720
Capture Interval: 10s
...

Running system validation...
✓ Device found: /dev/video0
✓ Device permissions OK
✓ Test capture successful
✓ System validation passed

Running single capture...
[INFO] SUCCESS: Captured img_20250110_143022.jpg

✓ Single capture test PASSED
```

### Verify Captured Image

```bash
# List captures
ls -lh captures/

# View latest capture (if GUI available)
display captures/img_*.jpg
```

---

## Step 7: Start Continuous Operation

### Start System

```bash
# Start continuous capture mode
./scripts/start.sh
```

**Expected Output:**
```
==========================================
Pi Camera Integration System
Starting Continuous Capture Mode
==========================================

Starting system...
✓ System started successfully (PID: 1234)

Monitor logs:
  tail -f logs/capture_log.txt
  tail -f /tmp/pi_camera_system.out

Stop system:
  ./scripts/stop.sh
```

### Monitor Operation

```bash
# Watch logs in real-time
tail -f logs/capture_log.txt

# Watch captures directory
watch -n 5 'ls -lh captures/ | tail -10'

# Check system status
ps aux | grep python3
```

### Stop System

```bash
# Gracefully stop system
./scripts/stop.sh
```

---

## Step 8: Enable Auto-Start (Optional)

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/picamera.service
```

**Service File Content:**
```ini
[Unit]
Description=Pi Camera Integration System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi-camera-integration-system
ExecStart=/usr/bin/python3 /home/pi/pi-camera-integration-system/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Note:** Adjust paths if your username or installation directory differs.

### Enable Service

```bash
# Create main.py if not exists (copied from start.sh)
nano main.py
# (Copy content from start.sh's main.py creation section)

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable picamera.service

# Start service
sudo systemctl start picamera.service

# Check status
sudo systemctl status picamera.service

# View logs
sudo journalctl -u picamera.service -f
```

---

## Step 9: Verify Installation

### System Health Check

```bash
# Check if system is running
ps aux | grep python3

# Check logs for errors
tail -50 logs/capture_log.txt | grep ERROR

# Check capture success rate
grep "SUCCESS" logs/capture_log.txt | wc -l
grep "ERROR" logs/capture_log.txt | wc -l

# Check disk usage
df -h
du -sh captures/
```

### Test All Functions

1. **Single Capture**: `./scripts/run_once.sh`
2. **Continuous Mode**: `./scripts/start.sh`, wait 1 min, `./scripts/stop.sh`
3. **Check Metrics**: Review final output from stop
4. **Verify Files**: Confirm images exist in `captures/`

---

## Step 10: Regular Maintenance

### Daily Tasks

```bash
# Monitor logs
tail logs/capture_log.txt

# Check disk space
df -h
```

### Weekly Tasks

```bash
# Review success rate
grep "SUCCESS\|ERROR" logs/capture_log.txt | tail -100

# Archive old captures
cd captures/
tar -czf archive_$(date +%Y%m%d).tar.gz *.jpg
mv archive_*.tar.gz ~/archives/

# Clean old captures
find . -name "*.jpg" -mtime +7 -delete
```

### Monthly Tasks

```bash
# System updates
sudo apt update && sudo apt upgrade -y

# Clear old logs
> logs/capture_log.txt

# Restart system for fresh start
sudo reboot
```

---

## Troubleshooting Setup Issues

### Camera Not Detected

```bash
# Reconnect camera
# Check dmesg for messages
dmesg | tail -20

# Try different USB port
# Use powered USB hub if needed
```

### Permission Errors

```bash
# Verify video group membership
groups | grep video

# If not member:
sudo usermod -a -G video $USER
# Log out and log back in
```

### Script Execution Errors

```bash
# Ensure scripts are executable
chmod +x scripts/*.sh

# Check Python path
which python3

# Verify all files present
ls -R
```

---

## Next Steps

After successful setup:

1. **Monitor for 24 Hours**
   - Watch logs for errors
   - Verify consistent capture
   - Check disk space growth

2. **Adjust Configuration**
   - Fine-tune capture interval
   - Adjust image quality
   - Modify cleanup settings

3. **Explore Documentation**
   - Read `docs/architecture.md`
   - Review `docs/troubleshooting.md`
   - Check `docs/roadmap.md` for future features

4. **Consider Enhancements**
   - Add remote monitoring
   - Implement cloud upload
   - Create web dashboard

---

## Quick Reference

### Essential Commands

```bash
# Test single capture
./scripts/run_once.sh

# Start continuous mode
./scripts/start.sh

# Stop system
./scripts/stop.sh

# View logs
tail -f logs/capture_log.txt

# Check status
ps aux | grep python3
```

### File Locations

- Configuration: `config/default_config.yaml`
- Captures: `captures/`
- Logs: `logs/capture_log.txt`
- Scripts: `scripts/`
- Source code: `src/`

---

## Getting Help

If you encounter issues:

1. Check `docs/troubleshooting.md`
2. Enable debug logging
3. Review complete logs
4. Verify hardware connections
5. Test camera manually with fswebcam

---

**Setup Complete! Your Pi Camera Integration System is ready for operation.**

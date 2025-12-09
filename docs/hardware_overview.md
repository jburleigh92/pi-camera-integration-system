# Hardware Overview

## System Components

### 1. Raspberry Pi 4

**Specifications:**
- **Model**: Raspberry Pi 4 Model B
- **CPU**: Broadcom BCM2711, Quad-core Cortex-A72 (ARM v8) 64-bit SoC @ 1.5GHz
- **RAM**: 2GB, 4GB, or 8GB LPDDR4-3200 SDRAM
- **Storage**: MicroSD card slot
- **USB**: 2× USB 3.0 ports, 2× USB 2.0 ports
- **GPIO**: 40-pin GPIO header
- **Power**: 5V DC via USB-C (minimum 3A supply)

**Recommended for this Project:**
- 4GB RAM model (2GB sufficient for basic operation)
- Class 10 microSD card, 32GB or larger
- Official Raspberry Pi power supply (5.1V, 3A)

**Role in System:**
- Main compute platform
- Runs Linux operating system
- Executes Python application
- Manages USB camera interface
- Stores captured images and logs

---

### 2. USB Webcam

**Requirements:**
- **Interface**: USB 2.0 or 3.0
- **Driver Support**: V4L2 (Video4Linux2) compatible
- **Resolution**: 640x480 minimum, 1920x1080 recommended
- **Frame Rate**: 15 FPS minimum, 30 FPS recommended
- **Power**: USB bus-powered or external power

**Recommended Models:**
- Logitech C270 (720p, reliable V4L2 support)
- Logitech C920 (1080p, excellent quality)
- Microsoft LifeCam HD-3000 (720p, good compatibility)
- Generic UVC webcams (most work with V4L2)

**Testing Compatibility:**
```bash
# Check if camera is detected
lsusb

# Verify V4L2 device creation
ls -l /dev/video*

# Test capture
fswebcam -d /dev/video0 -r 1280x720 test.jpg
```

**Role in System:**
- Image capture device
- Provides live video feed
- Controlled via V4L2 driver
- Exposed as /dev/video0 (or similar)

---

### 3. Storage (MicroSD Card)

**Specifications:**
- **Capacity**: 32GB recommended (16GB minimum)
- **Speed Class**: Class 10 or UHS-I
- **Type**: MicroSD/MicroSDHC/MicroSDXC
- **Reliability**: High-endurance card recommended for continuous writing

**Recommended Models:**
- SanDisk Extreme (A2, V30)
- Samsung EVO Plus (U3, Class 10)
- Kingston Canvas React (V30, A1)

**Storage Breakdown:**

| Component | Estimated Size |
|-----------|----------------|
| Operating System | 4-6 GB |
| System Software | 1-2 GB |
| Application Code | <100 MB |
| Logs | 1-5 MB/day |
| Images (1280x720) | 200-300 KB each |
| Available for Captures | ~20-25 GB |

**Capacity Planning:**

At 10-second intervals (default):
- Images per hour: 360
- Images per day: 8,640
- Storage per day (300KB avg): ~2.6 GB
- Days until full (25GB): ~9-10 days

With 7-day auto-cleanup (default):
- Max storage used: ~18 GB
- Safe margin maintained

**Role in System:**
- Operating system storage
- Application code storage
- Captured image storage
- Log file storage
- Configuration persistence

---

### 4. Power Supply

**Requirements:**
- **Voltage**: 5V DC
- **Current**: 3A minimum (official supply provides 3A)
- **Connector**: USB-C
- **Regulation**: Stable power delivery

**Why 3A is Important:**
- Raspberry Pi 4 base: ~600mA
- USB peripherals: ~500mA per device
- Undervoltage causes:
  - System instability
  - USB device disconnects
  - Throttled CPU performance
  - Data corruption

**Monitoring Power:**
```bash
# Check for undervoltage warnings
vcgencmd get_throttled

# Output: 0x0 = No issues
# Output: 0x50000 = Undervoltage detected
```

**Role in System:**
- Provides stable power to Pi
- Prevents brownouts and crashes
- Ensures USB devices function properly

---

### 5. Networking (Optional)

**Options:**
- **Ethernet**: Gigabit Ethernet port (RJ45)
- **WiFi**: 2.4 GHz and 5.0 GHz IEEE 802.11ac wireless
- **Bluetooth**: Bluetooth 5.0, BLE

**Use Cases:**
- SSH remote access
- Configuration updates
- Log monitoring
- Future: Image upload to cloud

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────┐
│            Raspberry Pi 4                   │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │         Operating System              │ │
│  │     (Raspberry Pi OS Bullseye)        │ │
│  │                                       │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Python Application Layer       │ │ │
│  │  │  - Configuration Management     │ │ │
│  │  │  - Capture Orchestration        │ │ │
│  │  │  - Health Monitoring            │ │ │
│  │  │  - File Management              │ │ │
│  │  │  - Logging                      │ │ │
│  │  └──────────┬──────────────────────┘ │ │
│  │             ↓                         │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  fswebcam (System Binary)       │ │ │
│  │  └──────────┬──────────────────────┘ │ │
│  │             ↓                         │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  V4L2 Driver Layer              │ │ │
│  │  └──────────┬──────────────────────┘ │ │
│  │             ↓                         │ │
│  └─────────────┼─────────────────────────┘ │
│                ↓                           │
│    ┌───────────────────────┐              │
│    │    USB Controller     │              │
│    └───────────┬───────────┘              │
└────────────────┼──────────────────────────┘
                 ↓ USB Cable
         ┌───────────────┐
         │  USB Webcam   │
         └───────────────┘
```

---

## Physical Setup

### Mounting Options

**Desktop Setup:**
- Pi on desk/shelf
- Camera on small tripod or stand
- Direct view of target area

**Wall-Mount Setup:**
- Pi mounted in enclosure
- Camera mounted separately
- USB cable run between components
- Consider cable length (max 5m for USB 2.0)

**Portable Setup:**
- Pi in portable case
- Battery pack for power
- Camera attached to Pi
- For temporary deployments

### Cable Management

**USB Cable Considerations:**
- **Length**: Keep under 3 meters for USB 2.0
- **Quality**: Use shielded cables
- **Power**: Active USB extension cables for longer runs
- **Strain Relief**: Secure cables to prevent disconnection

**Best Practices:**
- Label cables for easy troubleshooting
- Use cable ties or clips
- Avoid sharp bends
- Keep away from power cables to reduce interference

---

## Environmental Considerations

### Operating Temperature
- **Raspberry Pi 4**: 0°C to 50°C (32°F to 122°F)
- **Typical Camera**: 0°C to 40°C (32°F to 104°F)

**Thermal Management:**
- Consider heatsinks for continuous operation
- Provide adequate ventilation
- Monitor CPU temperature:
  ```bash
  vcgencmd measure_temp
  ```

### Humidity
- **Safe Range**: 20-80% RH (non-condensing)
- **Protection**: Use enclosure in humid environments
- **Desiccant**: Consider for extreme conditions

### Vibration
- **Low**: Desktop, shelf mounting
- **Medium**: Vehicle mounting (use damping)
- **High**: Industrial environments (use ruggedized enclosures)

---

## Optional Hardware Additions

### 1. Case/Enclosure
**Purpose:**
- Physical protection
- Dust prevention
- Professional appearance
- Heat management

**Recommended:**
- Official Raspberry Pi 4 Case
- Argon ONE case (with fan)
- Custom 3D printed enclosures

### 2. Cooling Solution
**Options:**
- Passive heatsinks
- Active fan cooling
- Hybrid solutions

**When Needed:**
- Continuous operation
- Warm environments
- Overclocked systems

### 3. Real-Time Clock (RTC)
**Purpose:**
- Maintain accurate time without internet
- Important for timestamping

**Models:**
- DS3231 RTC module
- PCF8523 RTC

### 4. Powered USB Hub
**Purpose:**
- Multiple USB devices
- Provide adequate power to camera
- Prevent USB power issues

**When Needed:**
- High-power cameras
- Multiple peripherals
- Reliability improvement

### 5. Backup Power
**Options:**
- UPS (Uninterruptible Power Supply)
- Battery pack
- Supercapacitor for graceful shutdown

**Purpose:**
- Prevent data loss during power failure
- Allow graceful shutdown
- Continuous operation during outages

---

## Hardware Validation Checklist

Before deployment, verify:

- [ ] Raspberry Pi 4 boots successfully
- [ ] MicroSD card is properly seated
- [ ] USB camera is detected (`lsusb`)
- [ ] Video device appears (`/dev/video0`)
- [ ] Power supply provides stable voltage
- [ ] No undervoltage warnings
- [ ] Camera captures test image
- [ ] Storage has adequate space
- [ ] Network connectivity (if needed)
- [ ] All cables are secure
- [ ] Cooling is adequate (if needed)
- [ ] System runs for 1 hour without issues

---

## Maintenance Schedule

### Daily
- Visual inspection of connections
- Check LED indicators on Pi

### Weekly
- Verify camera operation
- Check for loose cables
- Clean camera lens if needed

### Monthly
- Dust cleaning
- Cable inspection
- Check SD card health
- Verify adequate cooling

### Quarterly
- Deep clean all components
- Replace thermal paste (if applicable)
- Check for firmware updates
- Test backup hardware (if available)

---

## Hardware Troubleshooting

### Pi Won't Boot
- Check power supply
- Try different microSD card
- Verify HDMI connection
- Check for damaged components

### Camera Not Working
- Try different USB port
- Test with different camera
- Check USB cable
- Verify power supply adequacy

### Intermittent Issues
- Check for undervoltage
- Verify adequate cooling
- Test with known-good hardware
- Check for loose connections

### Storage Issues
- Test SD card on different system
- Run filesystem check
- Consider SD card replacement
- Check for write errors in logs

---

## Recommended Hardware Kit

**Basic Setup (~$100-150):**
- Raspberry Pi 4 (4GB) - $55
- Official Power Supply - $8
- 32GB microSD Card - $10
- Logitech C270 Webcam - $25
- Official Pi 4 Case - $5
- Micro HDMI cable - $8
- Keyboard/Mouse (for setup) - $20

**Enhanced Setup (~$200-250):**
- All basic components
- Logitech C920 (1080p) - $70 (vs C270)
- Argon ONE case with fan - $25
- 64GB high-endurance SD - $20
- Powered USB hub - $15
- RTC module - $10

**Production Setup (~$300+):**
- All enhanced components
- Battery backup/UPS - $50
- External storage (USB SSD) - $50
- Multiple cameras support - varies
- Professional enclosure - $40

---

## Specifications Summary

| Component | Specification | Notes |
|-----------|--------------|-------|
| **CPU** | ARM Cortex-A72 @ 1.5GHz | Quad-core |
| **RAM** | 4GB LPDDR4 | 2GB minimum |
| **Storage** | 32GB microSD | Class 10+ |
| **USB Ports** | 4 total (2×USB3, 2×USB2) | Camera uses one |
| **Power** | 5V/3A USB-C | Official supply recommended |
| **Network** | Ethernet + WiFi | Optional for monitoring |
| **Camera** | V4L2-compatible USB | 720p minimum |
| **OS** | Raspberry Pi OS Bullseye | Legacy version |

---

**This hardware configuration provides a reliable, maintainable platform for industrial image capture applications.**

# 🚀 Pi Camera Integration System - QUICKSTART GUIDE

Get up and running in **5 minutes**!

---

## ⚡ Prerequisites

- Raspberry Pi 4 (or compatible)
- USB Webcam
- Raspberry Pi OS Bullseye (Legacy)
- Internet connection

---

## 📦 Installation (One Command)

```bash
cd pi-camera-integration-system
chmod +x scripts/*.sh
./scripts/install_dependencies.sh
```

This installs:
- ✅ fswebcam
- ✅ v4l-utils
- ✅ Python dependencies
- ✅ Adds you to `video` group

**Important**: Log out and back in after installation for group changes to take effect.

---

## 🎯 Quick Test (30 seconds)

Verify everything works with a single capture:

```bash
./scripts/run_once.sh
```

**Expected Output:**
```
✓ System validation passed
✓ Single capture test PASSED

Captured images: 1
Total size: 0.15 MB
Location: ./captures/
```

**Check the image:**
```bash
ls -lh captures/
```

---

## 🔄 Run Continuous Capture

Start the system in background mode:

```bash
./scripts/start.sh
```

**Monitor in real-time:**
```bash
tail -f logs/capture_log.txt
```

**Stop the system:**
```bash
./scripts/stop.sh
```

---

## 📊 Typical Log Output

```
[2025-01-10 14:03:22] SUCCESS: Captured img_20250110_140322.jpg
[2025-01-10 14:03:32] SUCCESS: Captured img_20250110_140332.jpg
[2025-01-10 14:03:42] ERROR: Capture failed (device busy). Retry 1/3
[2025-01-10 14:03:44] SUCCESS: Recovery successful after retry
```

---

## ⚙️ Configuration (Optional)

Edit `config/default_config.yaml` to customize:

```yaml
capture:
  interval: 10        # Seconds between captures
  retry_attempts: 3   # Max retries on failure
  
camera:
  resolution: "1280x720"  # Image resolution
  device: "/dev/video0"   # Camera device path
```

After editing, restart the system:
```bash
./scripts/stop.sh
./scripts/start.sh
```

---

## 🔍 Troubleshooting Quick Fixes

### Camera Not Found
```bash
# List available cameras
ls -l /dev/video*

# Update device in config if needed
# Edit config/default_config.yaml
```

### Permission Denied
```bash
# Ensure you're in video group
groups $USER

# If not listed, run:
sudo usermod -a -G video $USER
# Then log out and back in
```

### Check Device Info
```bash
v4l2-ctl --device /dev/video0 --all
```

### View All Logs
```bash
# Application log
tail -f logs/capture_log.txt

# System output (if running in background)
tail -f /tmp/pi_camera_system.out
```

---

## 📁 Where Files Are Stored

| Item | Location | Description |
|------|----------|-------------|
| Captured Images | `./captures/` | Timestamped JPEGs |
| Logs | `./logs/` | Rotating log files |
| Configuration | `./config/` | YAML settings |

---

## 🧪 Test Scenarios

### Simulate Camera Disconnect
1. Start continuous capture
2. Unplug USB camera
3. System logs: `CRITICAL: Camera disconnected!`
4. Plug camera back in
5. System logs: `Camera reconnected successfully`

### Stress Test (1 Hour)
```bash
# Run for 1 hour with 5-second intervals
# Captures ~720 images
# Monitors: success rate, memory usage, failures
```

---

## 📈 Health Metrics

While system is running, view metrics:

```bash
# In Python interpreter
python3
>>> from src.app.health_check import HealthCheck
>>> # Metrics shown during graceful shutdown
```

Or check logs for periodic health updates.

---

## 🛑 Graceful Shutdown

**Method 1:** Use stop script
```bash
./scripts/stop.sh
```

**Method 2:** If running in foreground
```bash
# Press Ctrl+C
# System will:
# 1. Finish current capture
# 2. Print final metrics
# 3. Clean up and exit
```

---

## 📚 Next Steps

Once you have the basics working:

1. **Read Full Docs**: `docs/setup_instructions.md`
2. **Understand Architecture**: `docs/architecture.md`
3. **Run Failure Tests**: `tests/failure_simulations.md`
4. **Check Roadmap**: `docs/roadmap.md`

---

## 💡 Pro Tips

### Tip 1: Check Disk Space
```bash
df -h
# Ensure adequate space for captures
```

### Tip 2: Monitor System Resources
```bash
# CPU and Memory
htop

# Disk I/O
iotop
```

### Tip 3: Automatic Startup on Boot
```bash
# Add to /etc/rc.local (before 'exit 0')
cd /path/to/pi-camera-integration-system
./scripts/start.sh
```

### Tip 4: Archive Old Captures
```bash
# Create dated archive
tar -czf captures_backup_$(date +%Y%m%d).tar.gz captures/

# Move archive to external storage
mv captures_backup_*.tar.gz /mnt/external/
```

---

## 🔧 Common Modifications

### Change Capture Interval
```yaml
# config/default_config.yaml
capture:
  interval: 5  # Change from 10 to 5 seconds
```

### Increase Image Quality
```yaml
# config/default_config.yaml
capture:
  quality: 95  # Change from 85 to 95
```

### Change Resolution
```yaml
# config/default_config.yaml
camera:
  resolution: "1920x1080"  # Change from 1280x720
```

---

## 📊 Expected Performance

| Configuration | Captures/Hour | Disk Space/Hour | Success Rate |
|---------------|---------------|-----------------|--------------|
| Default (10s) | 360 | ~50-70 MB | >99% |
| Fast (5s) | 720 | ~100-140 MB | >98% |
| Slow (30s) | 120 | ~20-30 MB | >99.5% |

---

## 🐛 Known Issues

1. **First capture may fail**: Camera warm-up issue
   - Solution: Retry logic handles this automatically

2. **"Device busy" after rapid captures**: Driver timing
   - Solution: Increase warmup_delay in config

3. **Permission errors**: User not in video group
   - Solution: `sudo usermod -a -G video $USER` and re-login

---

## 🆘 Getting Help

### Check Logs First
```bash
# Most recent errors
tail -n 50 logs/capture_log.txt
```

### Verbose Debugging
```yaml
# config/default_config.yaml
logging:
  level: "DEBUG"  # Change from INFO
```

### Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "Device not found" | Camera unplugged | Check USB connection |
| "Permission denied" | Not in video group | Add to group, re-login |
| "Timeout" | Slow camera | Increase capture_timeout |
| "File verification failed" | Disk full | Free up space |

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] User in `video` group (logged out/in)
- [ ] Camera connected (`ls /dev/video*`)
- [ ] Single capture test passed
- [ ] Continuous mode started
- [ ] Logs show successful captures
- [ ] Images appear in `captures/`

---

## 🎓 Learning Path

### Beginner (You are here!)
- [x] Install and run
- [x] Single capture test
- [x] View logs
- [ ] Understand configuration

### Intermediate
- [ ] Read architecture docs
- [ ] Run failure simulations
- [ ] Modify capture parameters
- [ ] Implement custom logging

### Advanced
- [ ] Add new camera backends (OpenCV)
- [ ] Integrate DSLR support
- [ ] Add network streaming
- [ ] Build ML quality scoring

---

## 🌟 You're All Set!

The system is now capturing images automatically. Explore the documentation in `docs/` to learn more about the architecture and capabilities.

**Questions?** Check `docs/troubleshooting.md`

**Want to extend it?** See `docs/roadmap.md` for ideas

**Happy Capturing! 📸**

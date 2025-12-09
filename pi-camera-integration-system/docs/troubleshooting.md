# Troubleshooting Guide

## Common Issues and Solutions

### Issue: Camera Not Detected

**Symptoms:**
- Error: "Device not found: /dev/video0"
- System validation fails
- No video devices listed

**Diagnosis:**
```bash
# Check if device exists
ls -l /dev/video*

# Check USB connections
lsusb

# Check kernel messages
dmesg | grep -i video
```

**Solutions:**

1. **Physical Connection**
   - Reconnect USB cable
   - Try different USB port
   - Check cable integrity

2. **Driver Issues**
   ```bash
   # Reload V4L2 module
   sudo modprobe -r uvcvideo
   sudo modprobe uvcvideo
   ```

3. **Check dmesg for errors**
   ```bash
   dmesg | tail -50
   ```

---

### Issue: Permission Denied

**Symptoms:**
- Error: "Insufficient permissions"
- "Permission denied" when accessing /dev/video0

**Diagnosis:**
```bash
# Check current user groups
groups

# Check device permissions
ls -l /dev/video0
```

**Solutions:**

1. **Add User to video Group**
   ```bash
   sudo usermod -a -G video $USER
   # Then log out and log back in
   ```

2. **Temporary Fix (until reboot)**
   ```bash
   sudo chmod 666 /dev/video0
   ```

3. **Run with sudo** (not recommended for production)
   ```bash
   sudo python3 main.py
   ```

---

### Issue: fswebcam Not Found

**Symptoms:**
- Error: "fswebcam not found - is it installed?"
- Command not found errors

**Diagnosis:**
```bash
# Check if installed
which fswebcam

# Check if in PATH
echo $PATH
```

**Solutions:**

1. **Install fswebcam**
   ```bash
   sudo apt update
   sudo apt install fswebcam -y
   ```

2. **Verify Installation**
   ```bash
   fswebcam --version
   ```

---

### Issue: Capture Timeout

**Symptoms:**
- Error: "Capture timeout after 10s"
- Long delays before failure
- Inconsistent capture success

**Causes:**
- Device initialization delay
- USB power issues
- Driver conflicts

**Solutions:**

1. **Increase Timeout**
   Edit `config/default_config.yaml`:
   ```yaml
   camera:
     capture_timeout: 20  # Increase from 10
   ```

2. **Increase Warm-up Delay**
   ```yaml
   camera:
     warmup_delay: 5  # Increase from 2
   ```

3. **Check USB Power**
   ```bash
   # Use powered USB hub
   # Check dmesg for USB power warnings
   dmesg | grep -i "power\|usb"
   ```

---

### Issue: Empty or Corrupted Images

**Symptoms:**
- Captured files are 0 bytes
- Images won't open
- "File verification failed"

**Diagnosis:**
```bash
# Check file size
ls -lh captures/

# Try to open with imagemagick
display captures/latest.jpg
```

**Solutions:**

1. **Check Disk Space**
   ```bash
   df -h
   ```

2. **Verify Camera Focus**
   - Check if camera lens is clear
   - Adjust camera position
   - Test with manual capture:
   ```bash
   fswebcam -r 1280x720 test.jpg
   ```

3. **Lower Resolution**
   ```yaml
   camera:
     resolution: "640x480"  # Try lower resolution
   ```

4. **Check JPEG Quality**
   ```yaml
   capture:
     quality: 85  # Try different values (1-100)
   ```

---

### Issue: Device Busy

**Symptoms:**
- Error: "Device or resource busy"
- Intermittent capture failures
- Works after waiting

**Causes:**
- Another process using camera
- Previous capture didn't clean up
- Driver still initializing

**Solutions:**

1. **Check for Other Processes**
   ```bash
   # List processes using camera
   sudo fuser /dev/video0
   
   # Kill if found
   sudo fuser -k /dev/video0
   ```

2. **Increase Retry Delay**
   ```yaml
   capture:
     retry_delay: 5  # Increase from 2
   ```

3. **Restart System**
   ```bash
   sudo reboot
   ```

---

### Issue: High Consecutive Failures

**Symptoms:**
- System reports "degraded" status
- Multiple failures in a row
- Eventually stops capturing

**Diagnosis:**
Check logs:
```bash
tail -50 logs/capture_log.txt
```

**Solutions:**

1. **Adjust Failure Threshold**
   ```yaml
   health:
     max_consecutive_failures: 10  # Increase from 5
   ```

2. **Check System Resources**
   ```bash
   # Check CPU/Memory
   htop
   
   # Check disk I/O
   iostat -x 1
   ```

3. **Reduce Capture Frequency**
   ```yaml
   capture:
     interval: 30  # Increase from 10
   ```

---

### Issue: Log Files Growing Too Large

**Symptoms:**
- Disk space filling up
- Large log files (>100 MB)
- System slowdown

**Solutions:**

1. **Adjust Log Rotation**
   ```yaml
   logging:
     max_log_size_mb: 5  # Reduce from 10
     backup_count: 2     # Reduce from 3
   ```

2. **Change Log Level**
   ```yaml
   logging:
     level: "WARNING"  # Change from "INFO"
   ```

3. **Manual Cleanup**
   ```bash
   # Clear old logs
   rm logs/capture_log.txt.*
   
   # Truncate current log
   > logs/capture_log.txt
   ```

---

### Issue: Cannot Stop System

**Symptoms:**
- `stop.sh` doesn't work
- Process still running
- PID file exists but process is dead

**Solutions:**

1. **Force Kill**
   ```bash
   # Find process
   ps aux | grep python3
   
   # Kill it
   kill -9 <PID>
   
   # Remove stale PID file
   rm /tmp/pi_camera_system.pid
   ```

2. **Check Script Permissions**
   ```bash
   chmod +x scripts/*.sh
   ```

---

### Issue: Captures Folder Growing Too Large

**Symptoms:**
- Disk space full
- Old images not being deleted
- System slows down

**Solutions:**

1. **Enable/Adjust Cleanup**
   ```yaml
   files:
     max_capture_age_days: 3  # Reduce from 7
   ```

2. **Manual Cleanup**
   ```bash
   # Delete captures older than 7 days
   find captures/ -name "*.jpg" -mtime +7 -delete
   ```

3. **Archive Old Captures**
   ```python
   # Run in Python
   from src.utils.file_manager import FileManager
   from src.app.config import Config
   
   config = Config().get_all()
   fm = FileManager(config, logger)
   fm.archive_captures()
   ```

---

## Advanced Diagnostics

### Camera Information

```bash
# List detailed camera info
v4l2-ctl --device /dev/video0 --all

# List supported formats
v4l2-ctl --device /dev/video0 --list-formats-ext
```

### System Resources

```bash
# Check CPU usage
top -bn1 | grep python

# Check memory
free -h

# Check disk
df -h

# Check USB tree
lsusb -t
```

### Network (for future remote features)

```bash
# Check network connectivity
ping -c 4 8.8.8.8

# Check open ports
netstat -tuln
```

---

## Error Code Reference

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| "Device not found" | Camera not connected | Check USB connection |
| "Permission denied" | User not in video group | Add to video group |
| "Device busy" | Another process using camera | Kill other process |
| "Capture timeout" | Command took too long | Increase timeout |
| "File verification failed" | Image not saved properly | Check disk space |
| "fswebcam not found" | Binary not installed | Install fswebcam |
| "Consecutive failures" | Multiple captures failed | Check device health |

---

## Getting Help

### Collect Debug Information

```bash
# System info
uname -a
cat /etc/os-release

# Camera info
lsusb
v4l2-ctl --device /dev/video0 --all

# Recent logs
tail -100 logs/capture_log.txt

# System output
cat /tmp/pi_camera_system.out
```

### Enable Debug Logging

Edit `config/default_config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

Then check logs for detailed information:
```bash
tail -f logs/capture_log.txt
```

---

## Preventive Maintenance

### Weekly Tasks
- [ ] Check disk space
- [ ] Review success rate metrics
- [ ] Archive old captures
- [ ] Clear old logs

### Monthly Tasks
- [ ] System updates
- [ ] Review configuration
- [ ] Test backup/restore
- [ ] Verify camera calibration

### As Needed
- [ ] Clean camera lens
- [ ] Check cable connections
- [ ] Update system software
- [ ] Review security patches

---

## Known Limitations

1. **Single Camera**: System supports only one camera at a time
2. **USB Power**: Some cameras require powered USB hub
3. **Resolution Limits**: Maximum resolution depends on camera
4. **No Hot-Swap**: Camera must be connected before startup
5. **Local Storage**: No built-in cloud upload (yet)

---

## Contact & Support

For issues not covered in this guide:

1. Check GitHub Issues
2. Review project documentation in `docs/`
3. Enable debug logging and collect logs
4. Submit detailed bug report with:
   - System information
   - Configuration files
   - Log excerpts
   - Steps to reproduce

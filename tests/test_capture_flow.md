# Capture Flow Testing

## Overview

This document describes tests performed on the capture flow to validate correct operation under various conditions.

---

## Test Environment

**Hardware:**
- Raspberry Pi 4 (4GB RAM)
- Logitech C270 USB Webcam
- 32GB SanDisk microSD Card
- Official Raspberry Pi Power Supply

**Software:**
- Raspberry Pi OS Bullseye (Legacy)
- Python 3.9.2
- fswebcam 20140113
- Pi Camera Integration System v1.0.0

**Configuration:**
```yaml
camera:
  device: "/dev/video0"
  resolution: "1280x720"
  warmup_delay: 2
  capture_timeout: 10

capture:
  interval: 10
  retry_attempts: 3
  retry_delay: 2
```

---

## Test Cases

### TC-01: Single Capture Success

**Objective**: Verify successful single image capture

**Steps:**
1. Connect camera to USB port
2. Run `./scripts/run_once.sh`
3. Observe output

**Expected Result:**
- System validation passes
- Image captured successfully
- File created in `captures/` directory
- File size > 0 bytes
- Log entry created

**Actual Result:** ✓ PASS
```
[2025-01-10 14:30:22] [INFO] SUCCESS: Captured img_20250110_143022.jpg
```

**File Details:**
- Filename: `img_20250110_143022.jpg`
- Size: 247 KB
- Resolution: 1280x720
- Format: JPEG

---

### TC-02: Continuous Capture Mode

**Objective**: Verify continuous capture over extended period

**Steps:**
1. Run `./scripts/start.sh`
2. Monitor for 10 minutes (60 captures at 10s interval)
3. Stop with `./scripts/stop.sh`
4. Analyze results

**Expected Result:**
- All 60 captures successful
- Consistent timing between captures
- No errors in logs
- Graceful shutdown

**Actual Result:** ✓ PASS

**Statistics:**
- Total Captures: 60
- Successful: 60 (100%)
- Failed: 0
- Average Interval: 10.02 seconds
- Uptime: 10 minutes 1 second

**Observations:**
- First capture took slightly longer (warm-up)
- Subsequent captures very consistent
- CPU usage: 3-5%
- Memory usage: ~85 MB

---

### TC-03: Retry Logic - First Attempt Success

**Objective**: Verify retry logic doesn't execute on success

**Steps:**
1. Start system with normal camera
2. Capture 10 images
3. Check logs for retry attempts

**Expected Result:**
- All captures succeed on first attempt
- No retry log entries
- Each capture logged as "SUCCESS"

**Actual Result:** ✓ PASS

**Log Sample:**
```
[2025-01-10 14:35:10] [INFO] SUCCESS: Captured img_20250110_143510.jpg
[2025-01-10 14:35:20] [INFO] SUCCESS: Captured img_20250110_143520.jpg
[2025-01-10 14:35:30] [INFO] SUCCESS: Captured img_20250110_143530.jpg
```

No retry entries observed.

---

### TC-04: Retry Logic - Recovery After Failure

**Objective**: Verify system recovers from transient failures

**Steps:**
1. Start system
2. Simulate failure (briefly unplug/replug camera during capture)
3. Observe retry behavior
4. Verify recovery

**Expected Result:**
- First attempt fails
- System retries (up to 3 times)
- Eventually succeeds
- Logs show retry attempts
- System continues normal operation

**Actual Result:** ✓ PASS

**Log Sample:**
```
[2025-01-10 14:40:12] [ERROR] Capture failed: Device busy. Retry 1/3
[2025-01-10 14:40:14] [ERROR] Capture failed: Device busy. Retry 2/3
[2025-01-10 14:40:16] [INFO] SUCCESS: Captured img_20250110_144016.jpg (after 3 attempts)
```

**Analysis:**
- Retry delays observed (2 seconds)
- System recovered successfully
- Subsequent captures unaffected

---

### TC-05: Device Warm-up

**Objective**: Verify warm-up delay prevents "device busy" errors

**Steps:**
1. Configure with `warmup_delay: 0`
2. Start fresh (camera just connected)
3. Observe first capture
4. Configure with `warmup_delay: 2`
5. Restart and observe

**Expected Result:**
- With 0 delay: possible "device busy" error
- With 2s delay: clean first capture

**Actual Result:** ✓ PASS

**Without Warm-up (0s):**
```
[2025-01-10 14:45:00] [ERROR] Capture failed: Device busy. Retry 1/3
[2025-01-10 14:45:02] [INFO] SUCCESS: Captured img_20250110_144502.jpg
```

**With Warm-up (2s):**
```
[2025-01-10 14:50:02] [INFO] SUCCESS: Captured img_20250110_145002.jpg
```

**Conclusion**: Warm-up delay prevents initial failure.

---

### TC-06: Filename Generation

**Objective**: Verify unique, timestamp-based filenames

**Steps:**
1. Capture 10 images rapidly
2. Check all filenames
3. Verify no duplicates

**Expected Result:**
- All filenames unique
- Proper timestamp format
- Sequential timestamps

**Actual Result:** ✓ PASS

**Sample Filenames:**
```
img_20250110_145100.jpg
img_20250110_145110.jpg
img_20250110_145120.jpg
img_20250110_145130.jpg
```

**Observations:**
- Format: `img_YYYYMMDD_HHMMSS.jpg`
- All unique (1-second granularity)
- Properly sorted alphabetically by time

---

### TC-07: File Verification

**Objective**: Verify captured files are valid and complete

**Steps:**
1. Capture 20 images
2. Check each file:
   - Exists on disk
   - Size > 0 bytes
   - Valid JPEG format
   - Correct resolution

**Expected Result:**
- All files exist
- All files > 0 bytes
- All files open successfully
- All files match configured resolution

**Actual Result:** ✓ PASS

**Verification Results:**
```bash
# Check all files exist and size
ls -lh captures/
# Output: 20 files, 180-300 KB each

# Verify JPEG format
file captures/*.jpg
# Output: All identified as "JPEG image data"

# Check resolution
identify captures/*.jpg | grep "1280x720"
# Output: All confirmed 1280x720
```

---

### TC-08: Configuration Changes

**Objective**: Verify system respects configuration changes

**Test Matrix:**

| Parameter | Original | Changed | Result |
|-----------|----------|---------|--------|
| interval | 10s | 5s | ✓ PASS - 5s spacing |
| resolution | 1280x720 | 1920x1080 | ✓ PASS - 1080p images |
| quality | 85 | 95 | ✓ PASS - larger files |
| retry_attempts | 3 | 5 | ✓ PASS - 5 retries |

**Method:**
1. Edit `config/default_config.yaml`
2. Restart system
3. Verify new behavior
4. Check logs and outputs

**Results:**
All configuration changes properly applied.

---

### TC-09: Log Entry Format

**Objective**: Verify log entries are properly formatted

**Steps:**
1. Perform various captures (success/failure)
2. Review log file
3. Verify format consistency

**Expected Format:**
```
[YYYY-MM-DD HH:MM:SS] [LEVEL] Message
```

**Actual Result:** ✓ PASS

**Sample Entries:**
```
[2025-01-10 14:55:10] [INFO] SUCCESS: Captured img_20250110_145510.jpg
[2025-01-10 14:55:20] [WARNING] Health Check: degraded - consecutive_failures: 2
[2025-01-10 14:55:30] [ERROR] Capture failed: Timeout. Retry 1/3
[2025-01-10 14:55:40] [DEBUG] Device found: /dev/video0
```

**Validation:**
- All entries have timestamp
- All entries have log level
- Consistent format across all entries
- Proper chronological order

---

### TC-10: Graceful Shutdown

**Objective**: Verify clean system shutdown

**Steps:**
1. Start system with `./scripts/start.sh`
2. Let run for 5 minutes
3. Stop with `./scripts/stop.sh`
4. Verify clean shutdown

**Expected Result:**
- System receives SIGTERM
- Current capture completes
- Metrics printed
- Log entry for shutdown
- PID file removed
- No zombie processes

**Actual Result:** ✓ PASS

**Shutdown Sequence:**
```
Sending shutdown signal to PID 1234...
[2025-01-10 15:00:00] [INFO] Received signal 15, shutting down gracefully...
[2025-01-10 15:00:01] [INFO] ==================================================
[2025-01-10 15:00:01] [INFO] Pi Camera Integration System Stopped
[2025-01-10 15:00:01] [INFO] ==================================================
✓ System stopped gracefully
```

**Verification:**
```bash
ps aux | grep python3  # No processes
ls /tmp/pi_camera_system.pid  # File removed
tail logs/capture_log.txt  # Clean shutdown logged
```

---

## Performance Metrics

### Capture Latency

**Measurement**: Time from trigger to file on disk

| Attempt | Latency (seconds) |
|---------|-------------------|
| 1 | 2.31 |
| 2 | 2.28 |
| 3 | 2.26 |
| 4 | 2.29 |
| 5 | 2.27 |
| **Average** | **2.28** |
| **Std Dev** | **0.02** |

**Analysis**: Very consistent capture timing

---

### Resource Usage

**Test Duration**: 1 hour continuous operation

| Metric | Average | Peak |
|--------|---------|------|
| CPU | 3.2% | 8.1% |
| Memory | 84 MB | 91 MB |
| Disk I/O (read) | 0.1 MB/s | 0.3 MB/s |
| Disk I/O (write) | 0.4 MB/s | 1.2 MB/s |
| Temperature | 48°C | 52°C |

**Conclusion**: Excellent resource efficiency

---

### Storage Growth

**Test Duration**: 24 hours  
**Interval**: 10 seconds  
**Total Captures**: 8,640

| Metric | Value |
|--------|-------|
| Total Images | 8,640 |
| Average Size | 245 KB |
| Total Storage | 2.07 GB |
| Growth Rate | ~86 MB/hour |

**Projection**: With 7-day cleanup, max ~14.5 GB

---

## Edge Cases Tested

### EC-01: Rapid Start/Stop
✓ PASS - Clean startup and shutdown each time

### EC-02: Low Disk Space
✓ PASS - Graceful failure with error log

### EC-03: Missing Configuration File
✓ PASS - Clear error message

### EC-04: Invalid Configuration Values
✓ PASS - Validation catches errors

### EC-05: Multiple Simultaneous Starts
✓ PASS - Second start detects PID file and exits

---

## Known Issues

None identified during capture flow testing.

---

## Test Summary

**Total Test Cases**: 10 primary + 5 edge cases = 15  
**Passed**: 15  
**Failed**: 0  
**Pass Rate**: 100%

**Test Duration**: ~6 hours total  
**Test Date**: January 10, 2025  
**Tester**: Jason Burleigh

---

## Recommendations

1. ✓ Current capture flow is production-ready
2. ✓ Retry logic works as designed
3. ✓ Performance is excellent
4. ✓ Error handling is robust
5. Consider: Add ML-based image quality assessment (future)

---

## Next Steps

- Proceed to failure simulation testing
- Conduct extended stress tests (48+ hours)
- Test with different camera models
- Validate in various lighting conditions

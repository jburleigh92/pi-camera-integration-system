# Pi Camera Integration System - Project Structure

## 📁 Complete File Organization

This document provides a comprehensive overview of every file in the project and its purpose.

---

## Root Directory Files

### `README.md`
- Main project documentation
- Overview, architecture, setup instructions
- Entry point for understanding the project

### `LICENSE`
- MIT License
- Open source licensing terms

### `requirements.txt`
- Python package dependencies
- PyYAML, Pillow, optional OpenCV and gPhoto2

### `main.py` ⭐
- **Primary entry point for continuous capture mode**
- Initializes all system components
- Runs validation and starts capture loop
- Usage: `python3 main.py`

### `.gitignore`
- Git exclusion rules
- Prevents tracking of captures/, logs/, and temporary files

---

## `src/` - Source Code Directory

### `src/__init__.py`
- Package initialization
- Version and author metadata

### `src/app/` - Application Layer

#### `src/app/__init__.py`
- Exports main application classes
- Provides clean import interface

#### `src/app/config.py`
- **Configuration Management**
- Loads and validates YAML configuration
- Provides dot-notation access to settings
- Validates required fields

#### `src/app/camera_interface.py`
- **Hardware Interface Layer**
- Direct interaction with camera via fswebcam
- Device validation and permission checks
- Warm-up logic and capture execution
- Timeout handling and error detection

#### `src/app/health_check.py`
- **System Health Monitoring**
- Tracks success/failure metrics
- Monitors consecutive failures
- Detects camera disconnections
- Calculates uptime and success rate

#### `src/app/capture.py` ⭐
- **Main Orchestration Layer**
- Combines all components into capture system
- Implements retry logic with exponential backoff
- Manages capture loop and intervals
- Handles graceful shutdown (SIGINT/SIGTERM)
- Periodic health checks and cleanup

### `src/utils/` - Utility Layer

#### `src/utils/__init__.py`
- Exports utility classes

#### `src/utils/logger.py`
- **Centralized Logging System**
- File and console output
- Log rotation (10 MB max, 3 backups)
- Structured log methods for different event types
- Timestamped entries

#### `src/utils/file_manager.py`
- **File System Operations**
- Generates timestamped filenames
- Verifies file creation and size
- Automatic cleanup of old captures (configurable days)
- Archive creation for backups
- Storage statistics

---

## `config/` - Configuration Directory

### `config/default_config.yaml`
- **System Configuration**
- Camera settings (device, resolution, timeout)
- Capture settings (interval, retries, quality)
- File paths and naming patterns
- Logging configuration
- Health monitoring thresholds
- fswebcam CLI flags

**Key Settings:**
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
  quality: 85
```

---

## `scripts/` - Automation Scripts

### `scripts/install_dependencies.sh`
- **System Setup Script**
- Installs fswebcam, v4l-utils, Python packages
- Adds user to `video` group
- Verifies installation
- Lists available video devices

### `scripts/start.sh`
- **Background Service Launcher**
- Starts system in daemon mode
- Manages PID file for process tracking
- Creates main.py if missing
- Outputs to `/tmp/pi_camera_system.out`

### `scripts/stop.sh`
- **Graceful Shutdown Script**
- Sends SIGTERM for clean shutdown
- Waits up to 10 seconds
- Forces SIGKILL if needed
- Cleans up PID file

### `scripts/run_once.sh`
- **Single Capture Test**
- Creates and runs test_single.py
- Performs one capture cycle
- Shows validation results
- Displays capture statistics

---

## `captures/` - Image Storage

### `captures/.gitkeep`
- Preserves directory in git
- Images are ignored by `.gitignore`

**Runtime Contents:**
- Timestamped JPEG images
- Format: `img_YYYYMMDD_HHMMSS.jpg`
- Automatically cleaned after 7 days (configurable)

---

## `logs/` - Log Storage

### `logs/capture_log.txt`
- Main application log file
- Rotates at 10 MB (keeps 3 backups)
- Contains all INFO, WARNING, ERROR messages

**Log Format:**
```
[2025-01-10 14:03:22] [INFO] SUCCESS: Captured img_20250110_140322.jpg
[2025-01-10 14:03:32] [ERROR] Capture failed: device busy. Retry 1/3
```

---

## `docs/` - Documentation

### `docs/architecture.md`
- System architecture diagrams
- Component relationships
- Data flow overview
- Integration patterns

### `docs/data_flow.md`
- Detailed data flow diagrams
- Capture pipeline breakdown
- Error handling paths
- State transitions

### `docs/hardware_overview.md`
- Raspberry Pi 4 specifications
- USB webcam requirements
- V4L2 driver details
- Hardware setup guide

### `docs/setup_instructions.md`
- Step-by-step installation
- Dependency installation
- Configuration guide
- First capture walkthrough

### `docs/troubleshooting.md`
- Common errors and solutions
- Permission issues
- Device not found problems
- Timeout debugging
- Performance optimization

### `docs/roadmap.md`
- Future enhancements
- Planned features
- Technology upgrades
- Community contributions

---

## `tests/` - Testing Documentation

### `tests/test_capture_flow.md`
- End-to-end test scenarios
- Expected vs actual behavior
- Validation checklists

### `tests/failure_simulations.md`
- Deliberate failure scenarios
- Camera disconnect tests
- Timeout simulations
- Low power conditions
- Recovery procedures

### `tests/stress_test_results.md`
- Long-running stability tests
- 1-2 hour continuous capture results
- Memory usage tracking
- Failure rate analysis

---

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                   (Entry Point Orchestrator)                 │
└────┬──────────────────────────────────────────────────┬─────┘
     │                                                    │
     ├──> Config ──> Load YAML ──> Validate              │
     │                                                    │
     ├──> Logger ──> File Handler ──> Rotation           │
     │              └─> Console Handler                  │
     │                                                    │
     ├──> FileManager ──> Generate Names                 │
     │                  └─> Verify Files                 │
     │                  └─> Cleanup Old                  │
     │                                                    │
     ├──> CameraInterface ──> fswebcam CLI               │
     │                      └─> Device Check             │
     │                      └─> Permissions              │
     │                                                    │
     ├──> HealthCheck ──> Metrics Tracking               │
     │                  └─> Failure Detection            │
     │                                                    │
     └──> CaptureSystem ──┬──> Retry Logic               │
                          ├──> Capture Loop              │
                          ├──> Health Monitoring         │
                          └──> Graceful Shutdown ────────┘
```

---

## Execution Flows

### Normal Capture Flow
```
1. main.py loads configuration
2. Initializes all components (Logger, FileManager, Camera, Health)
3. Creates CaptureSystem with all dependencies
4. Runs system validation
5. Enters continuous capture loop:
   - Check camera health (if interval elapsed)
   - Generate timestamped filename
   - Attempt capture (with retries)
   - Verify file creation
   - Log result
   - Update health metrics
   - Sleep until next interval
6. On SIGINT/SIGTERM: graceful shutdown
7. Print final metrics and exit
```

### Error Recovery Flow
```
1. Capture fails
2. Log error with details
3. Wait retry_delay seconds
4. Retry capture (up to max_retries)
5. If all retries fail:
   - Record failure in health metrics
   - Increment consecutive_failures
   - Check if threshold exceeded
6. Next health check detects degraded state
7. If max_consecutive_failures reached:
   - Log critical error
   - System can shut down or alert
```

---

## Key Design Patterns

### 1. Dependency Injection
- Components receive dependencies via constructor
- Enables testing and modularity
- Example: `CaptureSystem(config, logger, camera, file_manager, health)`

### 2. Separation of Concerns
- **camera_interface.py**: Hardware interaction only
- **capture.py**: Orchestration logic
- **health_check.py**: Metrics and monitoring
- **logger.py**: Centralized logging
- **file_manager.py**: File operations

### 3. Configuration as Code
- All settings in YAML
- Single source of truth
- No hardcoded values in application logic

### 4. Graceful Degradation
- System continues with warnings if degraded
- Only stops on complete failure
- Health states: healthy → degraded → failed

### 5. Retry with Backoff
- Configurable retry attempts
- Delay between retries
- Prevents overwhelming failed hardware

---

## Development Workflow

### Adding a New Feature

1. **Configuration**: Add settings to `config/default_config.yaml`
2. **Implementation**: Create or modify module in `src/app/` or `src/utils/`
3. **Integration**: Update `main.py` or `capture.py` to use new feature
4. **Logging**: Add appropriate log messages
5. **Documentation**: Update relevant files in `docs/`
6. **Testing**: Create test scenario in `tests/`

### Example: Adding Email Alerts

1. Add to config:
```yaml
alerts:
  email_enabled: true
  smtp_server: "smtp.gmail.com"
  recipient: "admin@example.com"
```

2. Create `src/utils/alert_manager.py`
3. Integrate in `capture.py` on failures
4. Update `docs/setup_instructions.md`
5. Add test in `tests/`

---

## File Size Reference

| File Category | Typical Size | Notes |
|---------------|--------------|-------|
| Python source | 3-8 KB | Well-commented code |
| Documentation | 7-15 KB | Comprehensive guides |
| Configuration | 1-2 KB | YAML format |
| Shell scripts | 2-4 KB | Automation scripts |
| Captured images | 50-200 KB | 1280x720 JPEG, quality 85 |
| Log files | Grows to 10 MB | Then rotates |

---

## Dependencies Graph

```
main.py
  ├─> src.app.config
  ├─> src.app.camera_interface
  ├─> src.app.health_check
  ├─> src.app.capture
  ├─> src.utils.logger
  └─> src.utils.file_manager

capture.py
  ├─> All injected dependencies
  └─> Uses: config, logger, camera, file_manager, health

camera_interface.py
  ├─> subprocess (fswebcam)
  └─> Uses: config, logger

health_check.py
  ├─> datetime
  └─> Uses: config, logger, camera

file_manager.py
  ├─> os, pathlib, shutil, datetime
  └─> Uses: config, logger

logger.py
  ├─> logging, logging.handlers
  └─> Uses: config
```

---

## Quick Reference

### Start System
```bash
./scripts/start.sh
```

### Stop System
```bash
./scripts/stop.sh
```

### Test Single Capture
```bash
./scripts/run_once.sh
```

### View Logs
```bash
tail -f logs/capture_log.txt
```

### Check Running Process
```bash
cat /tmp/pi_camera_system.pid
ps aux | grep main.py
```

---

## Environment Variables

None currently used. All configuration via YAML.

Potential future additions:
- `PI_CAMERA_CONFIG_PATH`: Override config file location
- `PI_CAMERA_LOG_LEVEL`: Override log level
- `PI_CAMERA_DEVICE`: Override camera device

---

## Security Considerations

1. **Permissions**: User must be in `video` group
2. **File Access**: Captures stored in user-accessible directory
3. **Logs**: May contain sensitive debugging information
4. **PID File**: World-readable in /tmp (consider `/var/run`)
5. **No Authentication**: Direct hardware access (single-user system)

---

## Performance Characteristics

| Metric | Typical Value | Notes |
|--------|---------------|-------|
| Capture Time | 1-3 seconds | Depends on camera and resolution |
| CPU Usage | 5-15% | During capture, <1% idle |
| Memory Usage | 30-50 MB | Python interpreter + libraries |
| Disk Usage | 50-200 KB/image | 1280x720 JPEG quality 85 |
| Startup Time | 2-4 seconds | Includes validation |

---

## Version History

- **v1.0.0** (2025-01): Initial release
  - Core capture system
  - Health monitoring
  - Retry logic
  - Documentation suite

---

This project structure follows industry best practices for:
- Systems integration
- Hardware/software interfaces
- Production-grade reliability
- Maintainable codebases
- Clear separation of concerns

Perfect for demonstrating capabilities in embedded systems, automation, and integration engineering roles.

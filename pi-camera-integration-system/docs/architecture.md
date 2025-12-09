# System Architecture

## Overview

The Pi Camera Integration System is designed as a modular, layered architecture that separates hardware interaction, application logic, and utilities. This design follows industry best practices for embedded systems and IoT devices.

## Architecture Layers

### 1. Hardware Layer
- **Raspberry Pi 4**: Main compute platform
- **USB Webcam**: V4L2-compatible image capture device
- **USB Interface**: Physical connection between Pi and camera

### 2. Operating System Layer
- **Linux Kernel**: Raspberry Pi OS (Bullseye Legacy)
- **V4L2 Drivers**: Video4Linux2 driver stack for camera access
- **Device Node**: `/dev/video0` (or similar) for camera communication

### 3. System Interface Layer
- **fswebcam**: Command-line image capture utility
- **v4l2-ctl**: Device configuration and diagnostics tool
- **Subprocess**: Python interface to system commands

### 4. Application Layer

#### Core Modules

**Config Management** (`config.py`)
- YAML configuration loading
- Runtime parameter validation
- Configuration hot-reload capability

**Camera Interface** (`camera_interface.py`)
- Device presence detection
- Permission verification
- Capture command execution
- Timeout handling
- Device information queries

**Health Monitoring** (`health_check.py`)
- Success/failure rate tracking
- Consecutive failure detection
- System uptime monitoring
- Alert generation
- Metrics collection and reporting

**Capture Orchestration** (`capture.py`)
- Main event loop
- Retry logic implementation
- Graceful shutdown handling
- System validation
- Integration of all subsystems

#### Utility Modules

**Logger** (`logger.py`)
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output
- Log rotation
- Structured log messages

**File Manager** (`file_manager.py`)
- Timestamped filename generation
- Directory management
- Old file cleanup
- File verification
- Storage statistics

## Data Flow

```
User Start Command
        ↓
System Validation
        ↓
Configuration Loading
        ↓
Component Initialization
        ↓
    ┌─────────────┐
    │ Main Loop   │
    └──────┬──────┘
           ↓
    ┌─────────────┐
    │Health Check │
    └──────┬──────┘
           ↓
    ┌─────────────┐
    │ Warm-up     │
    └──────┬──────┘
           ↓
    ┌─────────────┐
    │  Capture    │
    └──────┬──────┘
           ↓
    Success? ──No→ Retry Logic ──┐
           ↓ Yes                  │
    ┌─────────────┐              │
    │ File Verify │              │
    └──────┬──────┘              │
           ↓                      │
    ┌─────────────┐              │
    │   Logging   │←─────────────┘
    └──────┬──────┘
           ↓
    ┌─────────────┐
    │ Wait/Sleep  │
    └──────┬──────┘
           ↓
    (Loop back or Exit)
```

## Component Interactions

### Initialization Sequence

1. Load YAML configuration
2. Initialize logger
3. Create file manager (verify directories)
4. Initialize camera interface
5. Create health monitor
6. Build capture system
7. Run system validation
8. Enter main loop

### Capture Cycle

1. **Health Check Phase**
   - Verify device presence
   - Check permissions
   - Evaluate failure count
   - Determine system status

2. **Preparation Phase**
   - Camera warm-up delay
   - Generate output filename
   - Clear previous errors

3. **Capture Phase**
   - Execute fswebcam command
   - Monitor for timeout
   - Capture stdout/stderr
   - Parse return code

4. **Validation Phase**
   - Verify file exists
   - Check file size > 0
   - Validate file integrity

5. **Retry Phase** (if needed)
   - Log failure details
   - Increment attempt counter
   - Wait retry delay
   - Repeat from Capture Phase

6. **Recording Phase**
   - Update success/failure metrics
   - Log capture event
   - Update health statistics
   - Trigger cleanup if needed

## Error Handling Strategy

### Failure Categories

**Recoverable Errors** (retry)
- Device temporarily busy
- Capture timeout
- Empty/corrupt output file
- Insufficient resources

**Non-Recoverable Errors** (abort)
- Device not present
- Permission denied
- Missing fswebcam binary
- Configuration errors

### Retry Logic

```
Max retries: 3 (configurable)
Retry delay: 2 seconds (configurable)

Attempt 1 → Fail → Wait 2s
Attempt 2 → Fail → Wait 2s
Attempt 3 → Fail → Record failure
```

### Health Degradation

```
Consecutive Failures: 0-2 → Healthy
Consecutive Failures: 3-4 → Degraded (Warning)
Consecutive Failures: 5+  → Failed (Critical)
```

## Scalability Considerations

### Current Limitations
- Single camera support
- Fixed capture interval
- Local storage only
- No remote monitoring

### Future Extensions
- Multi-camera support
- Dynamic interval adjustment
- Cloud storage integration
- Real-time streaming
- Distributed deployment
- Container orchestration

## Security Model

### Access Control
- Requires membership in `video` group
- Read/write access to `/dev/video*`
- File system permissions for capture directory

### Data Protection
- Local file storage (no network transmission by default)
- Log rotation prevents disk exhaustion
- Old capture cleanup prevents storage overflow

## Performance Profile

### Resource Usage
- **CPU**: <5% during capture, <1% idle
- **Memory**: ~50-100 MB Python process
- **Disk I/O**: Burst during capture, minimal otherwise
- **Network**: None (unless extended)

### Timing
- Capture latency: 1-3 seconds
- Warm-up delay: 2 seconds (configurable)
- Health check: <1 second
- Total cycle time: 10 seconds (configurable)

## Deployment Architecture

### Standalone Mode
```
Raspberry Pi
    ├── Python Application
    ├── fswebcam
    ├── Local Storage
    └── Local Logs
```

### Future: Distributed Mode
```
Raspberry Pi (Edge)
    ├── Python Application
    ├── fswebcam
    └── Local Buffer
          ↓
    (MQTT/Kafka)
          ↓
Central Server
    ├── Image Processing
    ├── Long-term Storage
    └── Dashboard
```

## Technology Stack

- **Language**: Python 3.7+
- **System Utility**: fswebcam (C binary)
- **Configuration**: YAML
- **Logging**: Python logging module
- **Process Control**: Linux signals (SIGTERM, SIGINT)
- **Storage**: Local filesystem
- **OS**: Raspberry Pi OS (Debian-based)

## Design Patterns

1. **Factory Pattern**: Component initialization
2. **Strategy Pattern**: Configurable retry logic
3. **Observer Pattern**: Health monitoring and alerting
4. **Singleton Pattern**: Logger instance
5. **Template Method**: Capture cycle execution

## Testing Strategy

- **Unit Tests**: Individual module validation
- **Integration Tests**: End-to-end capture flow
- **Stress Tests**: Extended runtime (1-2 hours)
- **Failure Simulation**: Device disconnect scenarios
- **Performance Tests**: Capture latency measurement

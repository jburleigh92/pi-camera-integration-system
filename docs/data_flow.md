# Data Flow Documentation

## Overview

This document describes how data moves through the Pi Camera Integration System, from user input through configuration, capture execution, file storage, and logging.

## High-Level Data Flow

```
Configuration (YAML) → Application State → Camera Commands → Image Files → Logs
```

## Detailed Flow Diagrams

### 1. System Startup Flow

```
┌──────────────────┐
│ User executes    │
│ start.sh         │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Load             │
│ default_config   │
│ .yaml            │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Parse YAML into  │
│ Python dict      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Validate         │
│ required fields  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Initialize       │
│ Logger           │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Create capture/  │
│ logs directories │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Initialize       │
│ all components   │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ System Ready     │
└──────────────────┘
```

### 2. Capture Execution Flow

```
┌──────────────────────────┐
│ Timer Triggers Capture   │
└─────────────┬────────────┘
              ↓
┌──────────────────────────┐
│ Generate Timestamp       │
│ Format: YYYYMMDD_HHMMSS  │
└─────────────┬────────────┘
              ↓
┌──────────────────────────┐
│ Build Full Output Path   │
│ ./captures/img_*.jpg     │
└─────────────┬────────────┘
              ↓
┌──────────────────────────┐
│ Construct fswebcam       │
│ Command with Parameters  │
└─────────────┬────────────┘
              ↓
┌──────────────────────────┐
│ Execute Subprocess       │
│ with Timeout             │
└─────────────┬────────────┘
              ↓
        Success? ─────No───→ Error Handler
              ↓ Yes                ↓
┌──────────────────────────┐      ↓
│ Verify File Exists       │      ↓
└─────────────┬────────────┘      ↓
              ↓                    ↓
        Valid? ──────No───→ Error Handler
              ↓ Yes                ↓
┌──────────────────────────┐      ↓
│ Log Success              │      ↓
│ Update Metrics           │      ↓
└─────────────┬────────────┘      ↓
              ↓                    ↓
┌──────────────────────────┐      ↓
│ Return to Main Loop      │←─────┘
└──────────────────────────┘
```

### 3. Configuration Data Flow

**YAML Format**
```yaml
camera:
  device: "/dev/video0"
  resolution: "1280x720"
```

**Parsed to Python Dictionary**
```python
{
    'camera': {
        'device': '/dev/video0',
        'resolution': '1280x720'
    }
}
```

**Accessed in Code**
```python
device = config['camera']['device']
# or
device = config.get('camera.device')
```

### 4. Image File Data Flow

**Generation**
```
Timestamp Generation
    ↓
Format String Application
    ↓
Path Construction
    ↓
"./captures/img_20250110_143022.jpg"
```

**Storage**
```
fswebcam Output
    ↓
Temp Buffer (in-memory)
    ↓
Write to Disk
    ↓
File System (ext4)
    ↓
./captures/ directory
```

**Verification**
```
os.path.exists(filepath)
    ↓
os.path.getsize(filepath) > 0
    ↓
Optional: PIL Image.open()
    ↓
Validation Complete
```

### 5. Logging Data Flow

**Log Event Generation**
```
Application Event
    ↓
logger.info("message")
    ↓
Python logging.Logger
    ↓
Formatter Applied
    ↓
"[2025-01-10 14:30:22] [INFO] message"
```

**Log Destination Flow**
```
Formatted Log Message
    ↓
    ├──→ Console Handler → stdout
    │
    └──→ File Handler → logs/capture_log.txt
            ↓
        File Size > Max?
            ↓ Yes
        Rotate Files
            ↓
        capture_log.txt.1
        capture_log.txt.2
        capture_log.txt.3
```

### 6. Health Metrics Data Flow

**Metric Collection**
```
Capture Attempt
    ↓
Result (Success/Fail)
    ↓
HealthCheck.record_capture_attempt()
    ↓
Update Counters:
    - total_captures++
    - successful_captures++ OR failed_captures++
    - consecutive_failures (reset or increment)
    ↓
Calculate Success Rate
    ↓
Store Timestamp
```

**Metric Retrieval**
```
HealthCheck.get_metrics()
    ↓
Dictionary Construction
    ↓
{
    'total_captures': 150,
    'success_rate': 98.67,
    'uptime_seconds': 3600,
    ...
}
    ↓
Formatting
    ↓
Display to User
```

## Data Structures

### Configuration Object
```python
{
    'camera': {
        'device': str,
        'resolution': str,
        'warmup_delay': int,
        'capture_timeout': int
    },
    'capture': {
        'interval': int,
        'retry_attempts': int,
        'retry_delay': int,
        'output_format': str,
        'quality': int
    },
    'files': {
        'capture_dir': str,
        'log_dir': str,
        'filename_pattern': str,
        'max_capture_age_days': int
    },
    'logging': {
        'level': str,
        'log_file': str,
        'console_output': bool,
        'max_log_size_mb': int,
        'backup_count': int
    },
    'health': {
        'check_interval': int,
        'max_consecutive_failures': int,
        'alert_on_disconnect': bool
    }
}
```

### Health Metrics Object
```python
{
    'uptime_seconds': int,
    'uptime_formatted': str,
    'total_captures': int,
    'successful_captures': int,
    'failed_captures': int,
    'success_rate': float,
    'consecutive_failures': int,
    'camera_disconnects': int,
    'last_success': str,  # timestamp
    'last_failure': str,  # timestamp
    'last_health_check': str  # timestamp
}
```

### Capture Result Object
```python
(success: bool, error_message: Optional[str])

# Examples:
(True, None)  # Success
(False, "Device busy")  # Failure with error
```

### File Stats Object
```python
{
    'count': int,  # Number of captures
    'total_size_mb': float,  # Total storage used
    'oldest': str,  # Timestamp of oldest capture
    'newest': str   # Timestamp of newest capture
}
```

## Data Persistence

### Temporary Data (Memory Only)
- Current system state
- Retry counters
- Active capture process
- In-flight metrics

### Session Data (Persists During Runtime)
- Cumulative metrics
- Health statistics
- Configuration (runtime modifications)

### Permanent Data (Persists Across Restarts)
- Configuration files (YAML)
- Captured images (JPEG)
- Log files (TXT)

## Data Volume Estimates

### Configuration
- **Size**: ~1 KB (YAML file)
- **Frequency**: Loaded once at startup
- **Growth**: Static

### Images
- **Size**: ~100-500 KB per image (depends on resolution/quality)
- **Frequency**: Every N seconds (configurable, default 10s)
- **Growth**: ~8-40 MB per hour at 10s intervals
- **Management**: Auto-cleanup after 7 days (configurable)

### Logs
- **Size**: ~50-100 bytes per log entry
- **Frequency**: Variable (multiple per capture)
- **Growth**: ~1-5 MB per day
- **Management**: Log rotation at 10 MB, keep 3 backups

## Data Transformation Points

### 1. YAML → Python Dict
**Transform**: `yaml.safe_load()`
**Location**: `config.py:_load_config()`
**Error Handling**: YAML parse errors, missing file

### 2. Timestamp → Filename
**Transform**: `datetime.strftime(pattern)`
**Location**: `file_manager.py:generate_filename()`
**Format**: `img_%Y%m%d_%H%M%S.jpg`

### 3. Command Args → Shell Command
**Transform**: List to string via `subprocess`
**Location**: `camera_interface.py:capture_image()`
**Example**: `['fswebcam', '-r', '1280x720', ...]`

### 4. Metrics Dict → Formatted Output
**Transform**: String formatting
**Location**: `health_check.py:print_metrics()`
**Output**: Human-readable table

## Error Propagation

```
Low-Level Error (fswebcam)
    ↓
Captured by subprocess.run()
    ↓
Returned as (False, error_msg)
    ↓
Logged by logger.log_capture_failure()
    ↓
Recorded by health.record_capture_attempt(False)
    ↓
Potentially triggers alert
    ↓
May cause system shutdown (if consecutive failures)
```

## Data Security Considerations

### Current Implementation
- **Local storage only**: No network transmission
- **File permissions**: Respect system umask
- **Log rotation**: Prevents disk exhaustion
- **No sensitive data**: Images and logs contain no PII

### Future Enhancements
- **Encryption at rest**: Encrypt captured images
- **Secure transmission**: HTTPS/TLS for remote upload
- **Access control**: Authentication for web interface
- **Audit logging**: Track all access to captures

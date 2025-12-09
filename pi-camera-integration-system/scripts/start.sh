#!/bin/bash
# Pi Camera Integration System - Start Script

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Pi Camera Integration System"
echo "Starting Continuous Capture Mode"
echo "=========================================="
echo ""

# Check if already running
if [ -f "/tmp/pi_camera_system.pid" ]; then
    PID=$(cat /tmp/pi_camera_system.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Error: System is already running (PID: $PID)"
        echo "Run ./scripts/stop.sh to stop it first"
        exit 1
    else
        # Stale PID file, remove it
        rm /tmp/pi_camera_system.pid
    fi
fi

# Create main.py if it doesn't exist
if [ ! -f "main.py" ]; then
    echo "Creating main.py entry point..."
    cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
Pi Camera Integration System - Main Entry Point
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.config import Config
from app.camera_interface import CameraInterface
from app.health_check import HealthCheck
from app.capture import CaptureSystem
from utils.logger import Logger
from utils.file_manager import FileManager


def main():
    """Main entry point for continuous capture mode"""
    try:
        # Load configuration
        config = Config()
        config_dict = config.get_all()
        
        # Initialize components
        logger = Logger(config_dict)
        file_manager = FileManager(config_dict, logger)
        camera = CameraInterface(config_dict, logger)
        health_check = HealthCheck(config_dict, logger, camera)
        
        # Create capture system
        capture_system = CaptureSystem(
            config_dict,
            logger,
            camera,
            file_manager,
            health_check
        )
        
        # Validate system
        if not capture_system.validate_system():
            logger.error("System validation failed, exiting")
            sys.exit(1)
        
        # Run continuous capture
        capture_system.run_continuous()
    
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
EOF
    chmod +x main.py
fi

# Start system in background
echo "Starting system..."
nohup python3 main.py > /tmp/pi_camera_system.out 2>&1 &
PID=$!

# Save PID
echo $PID > /tmp/pi_camera_system.pid

# Wait a moment and check if still running
sleep 2
if ps -p $PID > /dev/null 2>&1; then
    echo "✓ System started successfully (PID: $PID)"
    echo ""
    echo "Monitor logs:"
    echo "  tail -f logs/capture_log.txt"
    echo "  tail -f /tmp/pi_camera_system.out"
    echo ""
    echo "Stop system:"
    echo "  ./scripts/stop.sh"
else
    echo "✗ System failed to start"
    echo "Check /tmp/pi_camera_system.out for errors"
    rm /tmp/pi_camera_system.pid
    exit 1
fi

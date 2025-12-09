#!/bin/bash
# Pi Camera Integration System - Stop Script

echo "=========================================="
echo "Pi Camera Integration System"
echo "Stopping Service"
echo "=========================================="
echo ""

# Check if PID file exists
if [ ! -f "/tmp/pi_camera_system.pid" ]; then
    echo "System is not running (no PID file found)"
    exit 0
fi

# Read PID
PID=$(cat /tmp/pi_camera_system.pid)

# Check if process exists
if ! ps -p $PID > /dev/null 2>&1; then
    echo "System is not running (stale PID file)"
    rm /tmp/pi_camera_system.pid
    exit 0
fi

# Send SIGTERM for graceful shutdown
echo "Sending shutdown signal to PID $PID..."
kill -TERM $PID

# Wait for process to stop (max 10 seconds)
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✓ System stopped gracefully"
        rm /tmp/pi_camera_system.pid
        exit 0
    fi
    sleep 1
done

# If still running, force kill
echo "Process did not stop gracefully, forcing shutdown..."
kill -KILL $PID

if ! ps -p $PID > /dev/null 2>&1; then
    echo "✓ System stopped (forced)"
    rm /tmp/pi_camera_system.pid
    exit 0
else
    echo "✗ Failed to stop system"
    exit 1
fi

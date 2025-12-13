#!/bin/bash
# Pi Camera Integration System - Single Capture Test

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Pi Camera Integration System"
echo "Single Capture Test"
echo "=========================================="
echo ""

# Create test script if it doesn't exist
if [ ! -f "test_single.py" ]; then
    cat > test_single.py << 'EOF'
#!/usr/bin/env python3
"""
Pi Camera Integration System - Single Capture Test
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
    """Run single capture test"""
    try:
        # Load configuration
        config = Config()
        config_dict = config.get_all()
        
        print("\nConfiguration:")
        config.print_summary()
        
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
            print("\n✗ System validation failed")
            sys.exit(1)
        
        # Run single capture
        success = capture_system.run_single_capture()
        
        if success:
            print("\n✓ Single capture test PASSED")
            
            # Show captured file
            stats = file_manager.get_capture_stats()
            if stats['count'] > 0:
                print(f"\nCaptured images: {stats['count']}")
                print(f"Total size: {stats['total_size_mb']} MB")
                print(f"Location: {config_dict['files']['capture_dir']}/")
            
            sys.exit(0)
        else:
            print("\n✗ Single capture test FAILED")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
EOF
    chmod +x test_single.py
fi

# Run test
python3 test_single.py

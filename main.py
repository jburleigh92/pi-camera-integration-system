#!/usr/bin/env python3
"""
Pi Camera Integration System - Main Entry Point
Handles continuous capture mode with health monitoring and graceful shutdown
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
        print("Loading configuration...")
        config = Config()
        config_dict = config.get_all()
        
        # Print configuration summary
        config.print_summary()
        
        # Initialize components
        print("\nInitializing system components...")
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
        print("\nRunning system validation...")
        if not capture_system.validate_system():
            logger.error("System validation failed, exiting")
            print("\n✗ System validation failed")
            print("Check the error messages above for details")
            sys.exit(1)
        
        print("\n✓ System validation passed")
        print("\nStarting continuous capture mode...")
        print("Press Ctrl+C to stop\n")
        
        # Run continuous capture
        capture_system.run_continuous()
    
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

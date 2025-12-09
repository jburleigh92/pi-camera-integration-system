"""
Capture System Module
Main orchestration layer for automated image capture
"""

import time
import signal
import sys


class CaptureSystem:
    """
    Main system orchestrator
    Manages capture loop, retries, health monitoring, and graceful shutdown
    """
    
    def __init__(self, config, logger, camera, file_manager, health_check):
        """
        Initialize capture system
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
            camera: CameraInterface instance
            file_manager: FileManager instance
            health_check: HealthCheck instance
        """
        self.config = config
        self.logger = logger
        self.camera = camera
        self.file_manager = file_manager
        self.health = health_check
        
        self.interval = config['capture']['interval']
        self.max_retries = config['capture']['retry_attempts']
        self.retry_delay = config['capture']['retry_delay']
        
        self.running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown on SIGINT and SIGTERM"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def capture_with_retry(self):
        """
        Attempt image capture with retry logic
        
        Returns:
            bool: True if capture succeeded (within retry limit)
        """
        output_path = self.file_manager.generate_filename()
        
        for attempt in range(1, self.max_retries + 1):
            success, error = self.camera.capture_image(output_path)
            
            if success:
                # Verify file was created
                if self.file_manager.verify_file_exists(output_path):
                    self.logger.log_capture_success(
                        self.file_manager._get_filename(output_path),
                        attempt
                    )
                    self.health.record_capture_attempt(True)
                    return True
                else:
                    error = "File verification failed"
            
            # Capture failed
            self.logger.log_capture_failure(error, attempt, self.max_retries)
            
            # Don't delay after last attempt
            if attempt < self.max_retries:
                time.sleep(self.retry_delay)
        
        # All retries exhausted
        self.health.record_capture_attempt(False)
        return False
    
    def run_single_capture(self):
        """
        Run a single capture cycle (for testing/manual execution)
        
        Returns:
            bool: True if capture succeeded
        """
        self.logger.info("Running single capture...")
        
        # Health check
        status, details = self.health.check_camera_health()
        self.logger.log_health_check(status, str(details) if details else None)
        
        if status == 'failed':
            self.logger.error("Camera health check failed, aborting capture")
            return False
        
        # Camera warm-up
        self.camera.warm_up()
        
        # Capture
        success = self.capture_with_retry()
        
        # Print metrics
        self.health.print_metrics()
        
        return success
    
    def run_continuous(self):
        """
        Run continuous capture loop
        Captures images at specified interval until stopped
        """
        self.running = True
        self.logger.log_system_start()
        
        # Initial health check
        status, details = self.health.check_camera_health()
        self.logger.log_health_check(status, str(details) if details else None)
        
        if status == 'failed':
            self.logger.critical("Initial health check failed, cannot start")
            return
        
        # Initial warm-up
        self.camera.warm_up()
        
        self.logger.info(f"Starting continuous capture (interval: {self.interval}s)")
        
        try:
            while self.running:
                # Periodic health check
                if self.health.should_run_health_check():
                    status, details = self.health.check_camera_health()
                    
                    if status == 'failed':
                        self.logger.critical("Health check failed, stopping system")
                        break
                    elif status == 'degraded':
                        self.logger.warning(f"System degraded: {details}")
                
                # Capture image
                self.capture_with_retry()
                
                # Cleanup old files periodically (every 10 captures)
                if self.health.total_captures % 10 == 0:
                    self.file_manager.cleanup_old_captures()
                
                # Wait for next interval
                if self.running:
                    time.sleep(self.interval)
        
        except Exception as e:
            self.logger.critical(f"Unexpected error in main loop: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the capture system gracefully"""
        if not self.running:
            return
        
        self.running = False
        self.logger.log_system_stop()
        
        # Print final metrics
        self.health.print_metrics()
        
        # Print capture statistics
        stats = self.file_manager.get_capture_stats()
        self.logger.info(f"Capture Stats: {stats['count']} files, {stats['total_size_mb']} MB")
    
    def validate_system(self):
        """
        Run comprehensive system validation before starting
        
        Returns:
            bool: True if system is ready
        """
        self.logger.info("Running system validation...")
        
        # Check device presence
        if not self.camera.is_device_present():
            self.logger.error("Validation failed: Camera device not found")
            return False
        
        # Check permissions
        if not self.camera.check_device_permissions():
            self.logger.error("Validation failed: Insufficient permissions")
            self.logger.info("Hint: Try running with sudo or add user to 'video' group")
            return False
        
        # List available devices
        devices = self.camera.list_available_devices()
        self.logger.info(f"Available video devices: {devices}")
        
        # Test capture
        if not self.camera.test_capture():
            self.logger.error("Validation failed: Test capture unsuccessful")
            return False
        
        # Check directories
        self.file_manager._ensure_directories()
        
        self.logger.info("System validation passed ✓")
        return True


# Helper method for FileManager (add to file_manager.py if needed)
def _get_filename(self, filepath):
    """Extract filename from full path"""
    import os
    return os.path.basename(filepath)
